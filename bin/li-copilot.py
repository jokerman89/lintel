#!/usr/bin/env python3
# component: copilot-repository-adapter
# implements: ADR-0024, ADR-0025
# intent: .claude/plans/copilot-enterprise-launch/spec.md
# constraints: stdlib only, no network, preserve project prose, preflight all writes
# last_intent_review: 2026-09-08
"""Deterministic Copilot adapter; standard library only, no network or shell calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile

SCHEMA = 1
INVENTORY = ".github/lintel/manifest.json"
BUNDLE = ".github/lintel"
PROTOCOL_START = b"<!-- LINTEL:SESSION-PROTOCOL:START -->"
PROTOCOL_END = b"<!-- LINTEL:SESSION-PROTOCOL:END -->"
COMPONENTS = ("bin", "lib", "skills", "agents", "templates", "scaffolding/01-foundation", "packs/_default")
DOCS = ("docs/the-cycle.md", "docs/precedence.md", "docs/compliance.md", "docs/architecture.md",
        "docs/GLOSSARY.md", "docs/spec-kit.md", "docs/getting-started.md", "docs/copilot.md",
        "docs/concepts/planner-as-module.md", "docs/concepts/agent-dispatch-rules.md", "docs/concepts/orientator.md")
TEXT_SUFFIXES = {".md", ".sh", ".bash", ".py", ".json", ".yaml", ".yml", ".csv", ".tsv", ".txt", ".template", ".base"}
ATTRIBUTES = (
    ".github/lintel/** text=auto eol=lf",
    ".github/skills/li-*/** text=auto eol=lf",
    ".github/agents/lintel-*.agent.md text eol=lf",
    ".github/instructions/lintel-session.instructions.md text eol=lf",
)
WORKFLOWS = {
    "welcome": "Use when joining a repository to inspect Lintel setup and choose a first workflow.",
    "cycle": "Use for a multi-step initiative that needs the complete Lintel planning, implementation, review and capture cycle.",
    "sense": "Use at session start to load relevant memory, inspect repository state and scope the request.",
    "scope": "Use when an initiative needs boundaries, dependencies and an appropriate planning depth.",
    "define": "Use when a request needs requirements, acceptance criteria and a concrete design before implementation.",
    "discover": "Use to map an existing repository, relevant architecture and reusable components before planning changes.",
    "plan": "Use to turn a design into a requirement-traced spec, dependency-ordered build cards and a cold-executor prompt.",
    "build": "Use to implement an authorized plan card by card with spec and quality review and verification evidence.",
    "review": "Use to review changes against the specification, engineering quality and the active policy.",
    "ship": "Use after review to prepare a verified change for a pull request or an explicitly authorized release.",
    "capture": "Use after delivery to record evidence, durable lessons and the next-session handoff.",
    "resume": "Use to resume an interrupted initiative from its saved plan, state and handoff.",
    "spec-kit": "Use when a project uses GitHub Spec Kit to connect its requirements and tasks to Lintel build and review evidence.",
}
AGENTS = {
    "planner": ("Plan requirements, specifications and executable build cards for a scoped initiative.", "plan"),
    "builder": ("Implement an authorized build card and produce verification evidence with focused changes.", "build"),
    "reviewer": ("Review a change independently for specification compliance, correctness and missing evidence.", "review"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    """Reject traversal, Windows drives, symlink/reparse parents, and non-directories."""
    rel = PurePosixPath(relative)
    if not relative or relative != rel.as_posix() or rel.is_absolute() or any(p in (".", "..") for p in rel.parts) or "\\" in relative or ":" in relative:
        raise ValueError(f"Unsafe managed path: {relative!r}")
    path = root
    for part in rel.parts:
        path = path / part
        if path.is_symlink() or (path.exists() and getattr(path.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError(f"Symlink/reparse point refused: {path}")
        if path != root / relative and path.exists() and not path.is_dir():
            raise ValueError(f"Parent is not a directory: {path}")
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"Path escapes target: {relative}")
    return path


def read_file(root: Path, relative: str) -> bytes:
    path = safe_path(root, relative)
    if not path.is_file():
        raise ValueError(f"Required source file is missing: {path}")
    return source_bytes(path)


def source_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix in TEXT_SUFFIXES or not path.suffix:
        data = data.replace(b"\r\n", b"\n")
    return data


def text_bytes(value: str) -> bytes:
    return value.rstrip().encode("utf-8") + b"\n"


def generate(source: Path, target: Path) -> tuple[dict[str, bytes], dict[str, bytes], str]:
    local = source == target
    files = {}
    # A deliberately scoped source bundle: never copy .git, user packs, runtime,
    # customer material, host settings, hooks, or this generated bundle recursively.
    if not local:
        for component in COMPONENTS:
            folder = safe_path(source, component)
            if not folder.is_dir():
                raise ValueError(f"Missing source component: {component}")
            for path in sorted(folder.rglob("*")):
                relative = path.relative_to(source).as_posix()
                safe_path(source, relative)
                if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                    files[f"{BUNDLE}/{relative}"] = source_bytes(path)
        for relative in ("LICENSE",) + DOCS:
            if (source / relative).is_file():
                files[f"{BUNDLE}/{relative}"] = read_file(source, relative)
        bridge = "shims/copilot/COPILOT.md" if (source / "shims/copilot/COPILOT.md").is_file() else "COPILOT.md"
        files[f"{BUNDLE}/COPILOT.md"] = read_file(source, bridge)
    # File-relative Markdown links work after copying and in clean cloud clones.
    skill_source = "../../.." if local else "../../lintel"
    bridge_skill = "../../../shims/copilot/COPILOT.md" if local else "../../lintel/COPILOT.md"
    bridge_instruction = "../shims/copilot/COPILOT.md" if local else "lintel/COPILOT.md"
    for name, description in WORKFLOWS.items():
        read_file(source, f"skills/{name}/SKILL.md")
        files[f".github/skills/li-{name}/SKILL.md"] = text_bytes(f"""---
name: li-{name}
description: {description}
---

# Lintel {name}

Read the [Copilot adapter contract]({bridge_skill}) first, then execute the
[canonical {name} workflow]({skill_source}/skills/{name}/SKILL.md) for the user's request.
Resolve source resources relative to that canonical file; write outputs to the working
repository. Follow the adapter's tool mapping, authorization and verification rules.
""")
    bridge_agent = "../../shims/copilot/COPILOT.md" if local else "../lintel/COPILOT.md"
    for name, (description, workflow) in AGENTS.items():
        files[f".github/agents/lintel-{name}.agent.md"] = text_bytes(f"""---
name: lintel-{name}
description: {description}
---

Read the [Copilot adapter contract]({bridge_agent}) and use the
[Lintel {workflow} skill](../skills/li-{workflow}/SKILL.md).
Keep the task bounded to the supplied requirements and repository context. Report
changed files, checks actually run, findings by severity, and unresolved limitations.
Do not claim independent review if you implemented the same change. If delegation
is unavailable, label the pass as self-review and retain the human review gate.
""")
    files[".github/instructions/lintel-session.instructions.md"] = text_bytes(f"""---
applyTo: "**"
---

This repository uses Lintel. Read [the Copilot adapter]({('../' + bridge_instruction)})
before a multi-step task. Load the repository's AGENTS.md and relevant memory and
decisions. Keep plans and durable lessons in .claude/; the directory name is shared
storage, not a requirement to use Claude Code. Use li-plan before substantive work,
li-build for authorized cards and li-review before delivery. Existing user authorization
remains valid; ask only for missing scope or a new permission boundary. Lintel instructions
and reviews complement host permissions and branch rules; they do not enforce them.
""")
    files[".github/copilot-instructions.md"] = text_bytes(f"""# Lintel repository instructions

Read [the repository instructions](../AGENTS.md), then the
[Copilot adapter contract]({bridge_instruction}) for multi-step work.

Use `/li-welcome` to inspect setup, `/li-plan` to create a spec and build cards,
`/li-build` to execute authorized cards, and `/li-review` to verify changes.
Use `/li-cycle` for the complete workflow and `/li-resume` to continue a saved plan.
If slash discovery is unavailable, ask Copilot to read the corresponding
`.github/skills/li-<name>/SKILL.md` and carry out its instructions.

Read project memory and relevant decisions before edits. Verify actual behavior and
report checks, outcomes and limitations. Keep secrets and customer data out of artifacts.
Repository instructions do not replace enterprise policy, tool permissions or human review.
""")
    # Foundation seed files are user-owned immediately; never upgrade or hash them.
    seeds = {
        "AGENTS.md": text_bytes("""# Repository agent instructions

This repository uses Lintel for planned, reviewable agent sessions. Read
[CORE-PRINCIPLES.md](CORE-PRINCIPLES.md), recent .claude/memory/lessons.md,
.claude/memory/working-state.md and relevant .claude/decisions/ before substantive work.
Keep the current task list in .claude/plans/todo.md. For an initiative, write plan.md,
spec.md and prompt.md under .claude/plans/<initiative>/ and record validation evidence.
Follow existing project instructions in CLAUDE.md when present; surface conflicts.
Customize this file with the project's purpose, ownership, build and test commands.
"""),
        "CLAUDE.md": text_bytes("""# Repository instructions

Project context and ownership live in [AGENTS.md](AGENTS.md). The shared session
protocol below is self-contained and applies to work in this repository.
Add project-specific commands and motivated deviations outside its marked block.
"""),
        "CORE-PRINCIPLES.md": read_file(source, "scaffolding/01-foundation/CORE-PRINCIPLES.md"),
        "EVOLUTION.md": read_file(source, "scaffolding/01-foundation/EVOLUTION.md"),
        ".claude/lintel-layout.yaml": b"layout_version: 5\n",
    }
    for relative in (".claude/memory/lessons.md", ".claude/memory/working-state.md", ".claude/memory/personas.md", ".claude/plans/todo.md", ".claude/decisions/README.md", ".claude/decisions/TEMPLATE.md"):
        seeds[relative] = read_file(source, "scaffolding/01-foundation/" + relative)
    if local:
        seeds = {}  # Lintel already has its foundation; never duplicate it at root.
    return files, seeds, "repository" if local else "vendored"


def load_inventory(target: Path) -> tuple[dict[str, str], dict[str, str]]:
    path = safe_path(target, INVENTORY)
    if not path.exists():
        return {}, {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(value, dict) or type(value.get("schema_version")) is not int
            or value["schema_version"] != SCHEMA or not isinstance(value.get("files"), dict)):
        raise ValueError("Unsupported or malformed Copilot inventory")
    for relative, sha in value["files"].items():
        safe_path(target, relative)
        if not (relative.startswith(".github/lintel/") or relative.startswith(".github/skills/li-") or relative.startswith(".github/agents/lintel-") or relative in (".github/copilot-instructions.md", ".github/instructions/lintel-session.instructions.md")):
            raise ValueError(f"Inventory path outside managed namespaces: {relative}")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise ValueError(f"Invalid inventory hash: {relative}")
    blocks = value.get("blocks", {})
    if not isinstance(blocks, dict):
        raise ValueError("Malformed protocol block inventory")
    for relative, sha in blocks.items():
        if relative not in ("AGENTS.md", "CLAUDE.md") or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise ValueError(f"Invalid protocol block inventory: {relative}")
    return value["files"], blocks


def protocol_updates(source: Path, target: Path, seeds: dict[str, bytes],
                     old_blocks: dict[str, str], checking: bool) -> tuple[dict[str, bytes], dict[str, str], list[str]]:
    """Manage only marked protocol blocks; preserve all surrounding project prose."""
    payload = read_file(source, "scaffolding/01-foundation/SESSION-PROTOCOL.md").decode("utf-8-sig").strip().encode("utf-8")
    block = PROTOCOL_START + b"\n" + payload + b"\n" + PROTOCOL_END
    updates, hashes, errors = {}, {}, []
    for relative in ("AGENTS.md", "CLAUDE.md"):
        path = safe_path(target, relative)
        if path.exists() and not path.is_file():
            errors.append(f"Not a regular protocol file: {relative}")
            continue
        original = path.read_bytes() if path.exists() else seeds[relative]
        starts, ends = original.count(PROTOCOL_START), original.count(PROTOCOL_END)
        if starts == ends == 0:
            if checking:
                errors.append(f"Missing session protocol block: {relative}")
            separator = b"\n" if original.endswith(b"\n") else b"\n\n"
            merged = original + separator + block + b"\n"
        elif starts == ends == 1 and original.index(PROTOCOL_START) < original.index(PROTOCOL_END):
            begin = original.index(PROTOCOL_START)
            end = original.index(PROTOCOL_END) + len(PROTOCOL_END)
            actual = original[begin:end].replace(b"\r\n", b"\n")
            expected = old_blocks.get(relative, digest(block))
            if digest(actual) != expected:
                errors.append(f"Modified session protocol block (preserved): {relative}")
            if checking and actual != block:
                errors.append(f"Outdated session protocol block: {relative}")
            merged = original[:begin] + block + original[end:]
        else:
            errors.append(f"Malformed session protocol markers (preserved): {relative}")
            continue
        updates[relative] = merged
        hashes[relative] = digest(block)
    return updates, hashes, errors


def verify_links(files: dict[str, bytes], target: Path) -> list[str]:
    missing = []
    for relative, data in files.items():
        if not (relative.startswith(".github/skills/li-") or relative.startswith(".github/agents/lintel-") or relative in (".github/copilot-instructions.md", ".github/instructions/lintel-session.instructions.md")):
            continue
        for link in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", data.decode("utf-8")):
            resolved = (target / relative).parent.joinpath(link).resolve()
            if not resolved.is_relative_to(target):
                missing.append(f"Escaping generated link: {relative} -> {link}")
                continue
            key = resolved.relative_to(target).as_posix()
            if key not in files and not resolved.is_file():
                missing.append(f"Missing generated link: {relative} -> {link}")
    return missing


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".lintel-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def runtime_ignore_errors(target: Path, ignore_text: str) -> list[str]:
    """Check the required rule and, in Git repos, its effective negation behavior."""
    if ".claude/runtime/" not in ignore_text.splitlines():
        return ["Missing .claude/runtime/ ignore rule; run init"]
    git = shutil.which("git")
    if git and (target / ".git").exists():
        result = subprocess.run(
            [git, "-c", "core.fsmonitor=false", "-C", str(target), "check-ignore",
             "--no-index", "--quiet", ".claude/runtime/.lintel-ignore-check"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode:
            return ["Git does not confirm .claude/runtime/ is ignored; review conflicting ignore rules"]
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "check"))
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path, default=None)
    args = parser.parse_args()
    target = args.target.resolve()
    # Executable-relative source is stable even after copilot-env sets LINTEL_HOME
    # to project runtime storage. A source override is explicit, never ambient.
    source = (args.source or Path(__file__).resolve().parent.parent).resolve()
    if not target.is_dir():
        raise ValueError(f"Target directory does not exist: {target}")
    files, seeds, mode = generate(source, target)
    old, old_blocks = load_inventory(target)
    errors = []
    block_updates, block_hashes = {}, {}
    if mode == "vendored":
        block_updates, block_hashes, block_errors = protocol_updates(source, target, seeds, old_blocks, args.command == "check")
        errors.extend(block_errors)
    # Preflight this user-owned file too, before any managed content is written.
    ignore = safe_path(target, ".gitignore")
    if ignore.exists() and not ignore.is_file():
        raise ValueError(".gitignore is not a regular file")
    existing_ignore = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    if args.command == "init" and ".claude/runtime/" in existing_ignore.splitlines():
        errors.extend(runtime_ignore_errors(target, existing_ignore))
    attributes = safe_path(target, ".gitattributes")
    if attributes.exists() and not attributes.is_file():
        raise ValueError(".gitattributes is not a regular file")
    existing_attributes = attributes.read_text(encoding="utf-8") if attributes.exists() else ""
    # Preserve a team's existing instruction file. A path-scoped additive entry
    # carries the Lintel pointer instead; unowned files are never adopted silently.
    entry = ".github/copilot-instructions.md"
    if safe_path(target, entry).exists() and entry not in old:
        files.pop(entry)
    attribute_rules = list(ATTRIBUTES)
    if entry in files:
        attribute_rules.append(".github/copilot-instructions.md text eol=lf")
    for relative in sorted(set(files) | set(old) | set(seeds)):
        path = safe_path(target, relative)
        if path.exists() and not path.is_file():
            errors.append(f"Not a regular file: {relative}")
            continue
        if relative in seeds:
            continue
        actual = digest(path.read_bytes()) if path.is_file() else None
        if relative in old and actual not in (None, old[relative]):
            errors.append(f"Modified managed file (preserved): {relative}")
        elif relative not in old and actual is not None:
            # Identical generated files may be checked into Lintel before inventory
            # creation; accepting exact bytes never overwrites custom content.
            if relative not in files or actual != digest(files[relative]):
                errors.append(f"Unmanaged collision (preserved): {relative}")
        if args.command == "check":
            if relative in files and actual != digest(files[relative]):
                errors.append(f"Missing or outdated managed file: {relative}")
            if relative in old and relative not in files:
                errors.append(f"Obsolete managed file: {relative}")
    if args.command == "check":
        for relative in seeds:
            if not safe_path(target, relative).is_file():
                errors.append(f"Missing foundation file: {relative}")
        if not old:
            errors.append("Copilot inventory is missing; run init")
        errors.extend(runtime_ignore_errors(target, existing_ignore))
        if any(rule not in existing_attributes.splitlines() for rule in attribute_rules):
            errors.append("Missing Copilot .gitattributes rules; run init")
    errors.extend(verify_links({**files, **seeds}, target))
    if errors:
        raise ValueError("\n".join(errors))
    if args.command == "check":
        print(f"Copilot kit verified: {len(files)} managed files; {mode} source; no live-host validation.")
        return
    # Everything above is read-only. Only write after the entire update passes.
    for relative, data in sorted(files.items()):
        path = safe_path(target, relative)
        if not path.exists() or path.read_bytes() != data:
            atomic_write(path, data)
    for relative, data in block_updates.items():
        path = safe_path(target, relative)
        if not path.exists() or path.read_bytes() != data:
            atomic_write(path, data)
    for relative, data in seeds.items():
        path = safe_path(target, relative)
        if not path.exists():
            atomic_write(path, data)
    for relative in sorted(set(old) - set(files)):
        path = safe_path(target, relative)
        if path.exists():
            path.unlink()
    if ".claude/runtime/" not in existing_ignore.splitlines():
        separator = "\n" if existing_ignore.endswith("\n") else "\n\n"
        atomic_write(ignore, (existing_ignore + separator + "# Lintel local session state\n.claude/runtime/\n").encode("utf-8"))
    missing_rules = [rule for rule in attribute_rules if rule not in existing_attributes.splitlines()]
    if missing_rules:
        separator = "\n" if existing_attributes.endswith("\n") else "\n\n"
        atomic_write(attributes, (existing_attributes + separator + "# Lintel portable Copilot kit\n" + "\n".join(missing_rules) + "\n").encode("utf-8"))
    inventory = {"schema_version": SCHEMA, "source_mode": mode, "hooks_installed": False,
                 "blocks": block_hashes,
                 "files": {relative: digest(data) for relative, data in sorted(files.items())}}
    atomic_write(safe_path(target, INVENTORY), text_bytes(json.dumps(inventory, indent=2, sort_keys=True)))
    print(f"Copilot kit ready: {len(files)} managed files; {mode} source. Commit .github/ and foundation files.")
    print("Start a new Copilot session; inspect /skills and select /li-welcome. No hooks or host permissions were changed.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
