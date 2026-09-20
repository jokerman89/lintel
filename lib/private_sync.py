"""Shared opt-in destination binding and Git operations for private sync."""
# component: lintel-private-sync
# implements: ADR-0005, ADR-0010
# intent: .claude/plans/universal-implementation/packages/P02.md
# constraints: explicit destinations only; never erase private content or legacy records
# last_intent_review: 2026-09-20

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
from urllib.request import url2pathname


class SyncError(Exception):
    """A refused operation or failed Git action; never reported as success."""


def git(directory: Path, *args: str, allowed: tuple[int, ...] = (0,)) -> str:
    result = subprocess.run(
        ["git", "-C", str(directory), *args],
        capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode not in allowed:
        detail = result.stderr.strip() or result.stdout.strip()
        raise SyncError(f"Git operation failed ({result.returncode}): {detail}")
    return result.stdout.rstrip("\r\n")


def destination(value: str, base: Path) -> str:
    if not value or value.startswith("-") or any(ord(char) < 32 for char in value):
        raise SyncError("The destination must be a nonempty Git URL or local path, not an option.")
    if re.match(r"^[A-Za-z]:[\\/]", value):
        return Path(value).resolve().as_posix()
    if "://" in value:
        parsed = urlsplit(value)
        if parsed.password or (parsed.scheme in ("http", "https") and parsed.username):
            raise SyncError("Use a credential-free remote URL and Git's credential manager.")
        # Git's file transport treats ? and # as path bytes, not URI suffixes.
        return value
    if re.match(r"^[^/\\:]+(?:@[^/\\:]+)?:", value):
        return value
    path = Path(value).expanduser()
    return (path if path.is_absolute() else base / path).resolve().as_posix()


@dataclass(frozen=True)
class Binding:
    schema_version: int
    enabled: bool
    url: str
    directory: str


def replace_file(path: Path, content: bytes) -> None:
    if path.is_symlink():
        raise SyncError(f"Refusing to replace symlinked private-sync file: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=f".{path.name}.", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def write_binding(path: Path, binding: Binding) -> None:
    replace_file(path, (json.dumps(asdict(binding), indent=2) + "\n").encode("utf-8"))


def read_binding(path: Path, directory: Path) -> Binding:
    if not path.is_file():
        raise SyncError("Sync is not enabled. Run setup <repo-url> explicitly.")
    if path.is_symlink():
        raise SyncError("Refusing a symlinked private-sync binding file.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as error:
        raise SyncError("Legacy or invalid sync configuration. Run setup <repo-url> explicitly.") from error
    if (
        not isinstance(data, dict)
        or type(data.get("schema_version")) is not int
        or data["schema_version"] != 1
        or type(data.get("enabled")) is not bool
        or not isinstance(data.get("url"), str)
        or not isinstance(data.get("directory"), str)
        or not data["directory"]
    ):
        raise SyncError("Invalid private-sync binding. Run setup <repo-url> explicitly.")
    if Path(data["directory"]).resolve() != directory:
        raise SyncError("Binding belongs to a different local cache. Run setup <repo-url> explicitly.")
    return Binding(1, data["enabled"], data["url"], data["directory"])


def require_repository(directory: Path) -> None:
    if not (directory / ".git").exists():
        raise SyncError("Local sync repository is not initialized. Run setup <repo-url>.")
    root = git(directory, "rev-parse", "--show-toplevel")
    if Path(root).resolve() != directory:
        raise SyncError("The private cache must be its own Git worktree.")


def verify_origin(directory: Path, url: str) -> None:
    expected = destination(url, directory)
    if expected != url:
        raise SyncError("Binding is not an explicit absolute path or URL. Run setup <repo-url>.")
    for options in (("--all",), ("--push", "--all")):
        actual = git(directory, "remote", "get-url", *options, "origin").splitlines()
        if actual != [expected]:
            raise SyncError(
                "Origin does not match the enabled destination (including push URLs and rewrites). "
                "No sync performed; run setup <repo-url> to select the destination explicitly."
            )


def require_binding(path: Path, directory: Path) -> Binding:
    binding = read_binding(path, directory)
    if not binding.enabled:
        raise SyncError("Sync is disabled. Run setup <repo-url> explicitly to re-enable it.")
    require_repository(directory)
    verify_origin(directory, binding.url)
    return binding


def clone_preserving_files(directory: Path, url: str) -> None:
    directory.parent.mkdir(parents=True, exist_ok=True)
    effective = git(directory.parent, "ls-remote", "--get-url", url)
    if effective != url:
        raise SyncError("Git rewrites the selected destination. Use its explicit final URL.")
    with tempfile.TemporaryDirectory(prefix=".lintel-private-sync-", dir=directory.parent) as temporary:
        clone = Path(temporary) / "cache"
        git(directory.parent, "clone", "--quiet", "--no-recurse-submodules",
            "--origin", "origin", "--", url, str(clone))
        verify_origin(clone, url)
        entries = [
            path for path in clone.rglob("*")
            if ".git" not in path.relative_to(clone).parts
        ]
        for source in entries:
            target = directory / source.relative_to(clone)
            if source.is_symlink():
                if target.is_symlink() and os.readlink(source) == os.readlink(target):
                    continue
                if not target.exists() and not target.is_symlink():
                    continue
                raise SyncError("Setup conflicts with an existing local symlink or file.")
            if target.is_symlink():
                raise SyncError("Setup cannot write through a local symlink; existing files are preserved.")
            if target.exists() and (
                source.is_dir() != target.is_dir()
                or (source.is_file() and source.read_bytes() != target.read_bytes())
            ):
                raise SyncError(
                    f"Setup conflicts with existing local file: {source.relative_to(clone)}. "
                    "Local content is preserved; reconcile it before setup."
                )
        directory.mkdir(parents=True, exist_ok=True)
        for source in entries:
            target = directory / source.relative_to(clone)
            if source.is_symlink():
                if not target.is_symlink():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.symlink_to(os.readlink(source))
            elif source.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.open("rb") as incoming, target.open("xb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing)
                shutil.copymode(source, target)
        (clone / ".git").rename(directory / ".git")


def setup(directory: Path, path: Path, selected: str) -> None:
    url = destination(selected, Path.cwd())
    if directory.exists() and not directory.is_dir():
        raise SyncError("The private cache path is not a directory.")
    if (directory / ".git").exists():
        require_repository(directory)
        write_binding(path, Binding(1, False, "", str(directory)))
        git(directory, "config", "--local", "--replace-all", "remote.origin.url", url)
        # An old pushurl must not survive a new explicit destination selection.
        git(directory, "config", "--local", "--unset-all", "remote.origin.pushurl", allowed=(0, 5))
    else:
        clone_preserving_files(directory, url)
    verify_origin(directory, url)
    write_binding(path, Binding(1, True, url, str(directory)))
    print(f"Sync enabled. Verified origin: {url}\nLocal content preserved at {directory}")


def project_record(project: Path) -> str:
    root = Path(git(project, "rev-parse", "--show-toplevel")).resolve()
    origins = git(root, "config", "--get-all", "remote.origin.url", allowed=(0, 1)).splitlines()
    if len(origins) > 1:
        raise SyncError("Project has multiple origin URLs; select one stable project origin first.")
    if origins:
        effective = git(root, "remote", "get-url", "--all", "origin").splitlines()
        if len(effective) != 1:
            raise SyncError("Project must have exactly one effective origin URL.")
        origin = destination(effective[0], root)
        if origin.startswith("file://"):
            parsed = urlsplit(origin)
            local = Path(url2pathname(parsed.path))
            # Only a lossless canonical file URI may share a plain local-path key.
            if not parsed.netloc and local.is_absolute() and local.as_uri() == origin:
                origin = local.resolve().as_posix()
        if "://" in origin:
            name = unquote(urlsplit(origin).path).rstrip("/").rsplit("/", 1)[-1]
            identity = origin
        elif re.match(r"^[^/\\:]+(?:@[^/\\:]+)?:", origin) and not re.match(r"^[A-Za-z]:/", origin):
            name = origin.split(":", 1)[1].rstrip("/").rsplit("/", 1)[-1]
            identity = origin
        else:
            name = Path(origin).name
            identity = os.path.normcase(str(Path(origin)))
        name = name.removesuffix(".git")
        # Do not guess that different URL spellings or local .git suffixes are aliases.
        identity = "origin:" + identity
    else:
        common = Path(git(root, "rev-parse", "--git-common-dir"))
        common = (root / common).resolve()
        identity = "local:" + os.path.normcase(str(common))
        name = common.parent.name
    readable = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-")[:60] or "project"
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return f"{readable}--{digest}.md"


def current_branch(directory: Path) -> str:
    branch = git(directory, "symbolic-ref", "--quiet", "HEAD")
    if not branch.startswith("refs/heads/"):
        raise SyncError("Private sync requires a local branch, not detached HEAD.")
    return branch


def push(kind: str, directory: Path, path: Path, project: Path | None, lessons: Path | None) -> None:
    require_binding(path, directory)
    branch = current_branch(directory)
    if kind == "lessons":
        if project is None or lessons is None or not lessons.is_file():
            raise SyncError("No lessons file in the selected repository.")
        selected = [project_record(project)]
    else:
        selected = sorted(set(filter(None, git(
            directory, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*.md"
        ).split("\0"))))
    staged = set(filter(None, git(directory, "diff", "--cached", "--name-only", "-z").split("\0")))
    if staged.difference(selected):
        raise SyncError("Unrelated staged files in the cache; commit or unstage them before private sync.")
    if kind == "lessons":
        replace_file(directory / selected[0], lessons.read_bytes())
    if selected:
        git(directory, "--literal-pathspecs", "add", "--all", "--", *selected)
        changed = git(directory, "diff", "--cached", "--name-only")
        if changed:
            git(directory, "commit", "--quiet", "-m", f"sync private {kind}")
    git(directory, "rev-parse", "--verify", "HEAD")
    require_binding(path, directory)
    # Always attempt the push: a prior failed transport may have left a local commit.
    git(directory, "-c", "remote.origin.mirror=false", "push", "--no-follow-tags",
        "--recurse-submodules=no", "origin", f"HEAD:{branch}")
    print(f"Pushed private {kind} to the verified origin.")


def pull(directory: Path, path: Path) -> None:
    require_binding(path, directory)
    branch = current_branch(directory)
    before = git(directory, "rev-parse", "--verify", "--quiet", "HEAD", allowed=(0, 1))
    # No destination ref: --refmap= suppresses even forced remote.origin.fetch mappings.
    git(directory, "fetch", "--refmap=", "--no-tags", "--no-prune", "--no-prune-tags",
        "--no-recurse-submodules", "--no-auto-maintenance", "origin", branch)
    fetched = git(directory, "rev-parse", "--verify", "FETCH_HEAD^{commit}")
    fast_forward = not before
    if before:
        common = git(directory, "merge-base", "--all", before, fetched, allowed=(0, 1)).splitlines()
        fast_forward = before in common
        if not fast_forward and fetched not in common:
            raise SyncError("Pull is not a fast-forward. Local history, index and content are preserved.")
    require_binding(path, directory)
    if current_branch(directory) != branch or git(
        directory, "rev-parse", "--verify", "--quiet", "HEAD", allowed=(0, 1)
    ) != before:
        raise SyncError("The local branch changed during fetch; refusing to apply fetched content.")
    if fast_forward:
        git(directory, "-c", "merge.autoStash=false", "merge", "--ff-only", "--no-autostash",
            "--no-edit", "--no-overwrite-ignore", "--no-squash", fetched)
    print(f"Pulled private records from the verified origin into {directory}.")


def status(directory: Path, path: Path) -> None:
    if not path.exists():
        print("Sync is not configured. Run setup <repo-url> to enable it.")
        return
    binding = read_binding(path, directory)
    if not binding.enabled:
        print(f"Sync is disabled. Local content is preserved at {directory}.")
        return
    require_binding(path, directory)
    count = sum(1 for record in directory.rglob("*.md") if ".git" not in record.relative_to(directory).parts)
    print(f"Sync enabled. Verified origin: {binding.url}\nLocal directory: {directory}\nFiles: {count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", required=True, choices=("roles", "lessons"))
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--binding", required=True, type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--lessons-file", type=Path)
    parser.add_argument("command", nargs="?", default="status")
    parser.add_argument("url", nargs="?")
    args = parser.parse_args()
    args.command = {
        "--push": "push", "--pull": "pull", "--status": "status",
        "--help": "help", "-h": "help",
    }.get(args.command, args.command)
    directory = args.directory.resolve()
    binding_path = args.binding.absolute()
    try:
        if args.command == "setup" and args.url:
            setup(directory, binding_path, args.url)
        elif args.url:
            raise SyncError("Only setup accepts a destination argument.")
        elif args.command == "push":
            push(args.kind, directory, binding_path, args.project_root, args.lessons_file)
        elif args.command == "pull":
            pull(directory, binding_path)
        elif args.command == "forget":
            write_binding(binding_path, Binding(1, False, "", str(directory)))
            print(f"Sync disabled. All local content and Git history preserved at {directory}.")
        elif args.command == "status":
            status(directory, binding_path)
        elif args.command == "help":
            print(
                f"li-{args.kind}-sync [setup <repo-url>|push|pull|status|forget]\n\n"
                "Opt-in sync to an operator-selected PRIVATE Git repository only.\n"
                "Setup verifies one fetch/push origin and preserves existing files/history.\n"
                "Legacy URL-only configuration needs explicit setup again; it cannot sync.\n"
                "Push/pull require an enabled, current binding. Forget disables, not deletes.\n"
                "Pull updates the private cache, never a project's lessons source.\n"
                "Lesson records use readable names plus stable origin identities; without\n"
                "an origin, identity uses the canonical Git directory. Old records stay.\n"
                f"Binding (JSON): {binding_path}\nLocal cache: {directory}"
            )
        else:
            raise SyncError(f"Usage: li-{args.kind}-sync [setup <repo-url>|push|pull|status|forget]")
    except (SyncError, OSError, ValueError) as error:
        print(f"ERROR: li-{args.kind}-sync: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
