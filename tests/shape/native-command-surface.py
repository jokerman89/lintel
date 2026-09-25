#!/usr/bin/env python3
# component: current-command-surface-check
# implements: ADR-0028
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: read-only current-tree check; historical records and notices are not routing
# last_intent_review: 2026-09-25
"""Check current workflow identities and literal local references, without executing them."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from urllib.parse import unquote


# Approved entry retirements, including expired central aliases. These are command
# identities, not a ban on words, client vendors, persisted data paths or attribution.
RETIRED_COMMANDS = frozenset("""
office-hours plan-ceo-review plan-eng-review plan-design-review plan-devex-review
devex-review plan-tune autoplan qa qa-only investigate codex learn lessons skillify
document-generate context-save context-restore context-warm-related context-warm-adrs
context-warm-sessions browse scrape open-managed-browser setup-browser-cookies make-pdf
design-consultation design-shotgun design-html design-review retro landing-report health
pair-agent careful code-unfreeze research plan-and-build review-and-ship help v4-migrate
personas-rotate match context-budgetwatch context-snapshot context-dump context-warmup
role-activate role-deactivate role-rotate role-frame role-deep-dive role-update
ta-api-design ta-boundary-review ta-complexity-audit ta-contract-collision
ta-dependency-graph ta-quality-attributes ta-scaling-plan
da-analytics-readiness da-data-contract-collision da-migration-plan da-query-pattern-audit
da-retention-policy da-schema-design da-sharding-plan
sc-audit-path sc-auth-flow sc-compliance-evidence sc-dependency-security sc-incident-runbook
sc-secret-management sc-threat-model
dh-capacity-headroom dh-cost-projection dh-deployment-plan dh-observability-spec
dh-on-call-playbook dh-rollback-strategy dh-sli-slo-spec
tq-chaos-plan tq-contract-test-design tq-coverage-audit tq-flaky-quarantine
tq-perf-budget-spec tq-regression-suite tq-test-pyramid-review
freeze unfreeze benchmark context-tokenwatch
""".split())

# Exceptions are exact files or typed evidence fields, never archival directories.
# The CLI reports every applied exception; none is a claim of review clearance.
SOURCE_EXCEPTIONS = {
    "tests/shape/native-command-surface.py": "The explicit retirement policy, not a routing consumer.",
    "tests/unit/native-command-surface.py": "Deliberate positive and negative regression fixtures.",
    "LICENSE": "The distributed project license must retain its original legal text.",
    "skills/design-dna/LICENSES/MIT-next-level-builder.txt": "Required notice for the retained design corpus.",
    "skills/design-dna/LICENSES/Apache-2.0-anthropic.txt": "Required license for the retained profile adaptation.",
}
IGNORED_DIRECTORIES = frozenset({".git", "node_modules", "__pycache__", ".venv", "venv"})
TEXT_SUFFIXES = frozenset({
    ".md", ".sh", ".ps1", ".py", ".json", ".yaml", ".yml", ".toml",
    ".js", ".mjs", ".txt", ".template", ".example",
})
HOST_SLASH_COMMANDS = frozenset({"help", "skills", "instructions", "plugins", "plugin"})
NAME = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*"
EXPLICIT_COMMAND = re.compile(rf"(?<![\w/:])(?:/li[:-]|skill:)(?P<name>{NAME})(?![\w-])", re.I)
NATIVE_COMMAND = re.compile(rf"(?<![\w/:-])li-(?P<name>{NAME})(?![\w.-])", re.I)
BARE_COMMAND = re.compile(rf"`/(?P<name>{NAME})(?=[\s`])", re.I)
NAMED_SKILL = re.compile(
    rf"(?:\b(?:skill|workflow|command)\s+[`'\"](?P<before>{NAME})[`'\"]|"
    rf"[`'\"](?P<after>{NAME})[`'\"]\s+skill\b)", re.I,
)
SKILL_FIELD = re.compile(rf"""(?:^|[\s{{,])["']?skill["']?\s*[:=]\s*["']?(?P<name>{NAME})(?=["'\s,}}]|$)""", re.I)
DISTINCTIVE_COMMAND = re.compile(
    r"(?<![\w/.-])(" + "|".join(re.escape(name) for name in sorted(RETIRED_COMMANDS)
                                if "-" in name) + r")(?![\w/.-])", re.I,
)
SKILL_PATH = re.compile(
    rf"(?<![\w-])(?P<prefix>\.(?:github|agents|gemini|claude|cursor|opencode)/skills/|skills/)"
    rf"(?P<name>(?:li:)?{NAME})(?P<tail>(?:/[a-zA-Z0-9_.%-]+)*)(?![\w-])"
)
LINK = re.compile(r"\[[^\]\n]*\]\((<?[^\s)]+>?)(?:\s+['\"][^)]*)?\)")
URL = re.compile(r"\b(?:https?|mailto):[^\s`<>)]+", re.I)
FORMER_HEADERS = frozenset({
    "old", "old name", "former", "former entry", "former entries",
    "retired entry", "retired entries", "removed entry", "removed entries",
})


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    code: str
    message: str


def frontmatter(text: str) -> list[str]:
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0] != "---":
        return []
    try:
        return lines[1:lines.index("---", 1)]
    except ValueError:
        return []


def declared_aliases(lines: list[str]) -> list[tuple[int, str]]:
    result = []
    in_aliases = False
    for index, line in enumerate(lines, 2):
        clean = line.split("#", 1)[0].rstrip()
        match = re.match(r"^(?:deprecated_aliases|v1_alias):\s*(.*)$", clean)
        if match:
            in_aliases = not match[1]
            result.extend((index, value.strip(" \t[]'\""))
                          for value in match[1].split(",") if value.strip(" \t[]'\""))
        elif in_aliases and re.match(r"^\s+-\s+", clean):
            result.append((index, re.sub(r"^\s+-\s+", "", clean).strip("'\"")))
        elif clean and not clean[0].isspace():
            in_aliases = False
    return result


def source_files(root: Path) -> list[Path]:
    if (root / ".git").exists():
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            capture_output=True, check=False,
        )
        if result.returncode:
            raise ValueError("Cannot enumerate the current tracked/untracked nonignored tree.")
        paths = sorted(set(result.stdout.decode("utf-8").split("\0")) - {""})
        return [root / relative for relative in paths
                if (root / relative).exists() and (
                    (root / relative).suffix in TEXT_SUFFIXES
                    or Path(relative).name in {"LICENSE", "NOTICE", "COPYING"}
                    or (not Path(relative).suffix and Path(relative).parent.name == "bin")
                )]
    # Synthetic fixture trees need no Git initialization or repository mutation.
    result = []
    for directory, folders, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        folders[:] = sorted(
            name for name in folders
            if name not in IGNORED_DIRECTORIES
            and not (parent / name).is_symlink()
            and not getattr((parent / name).lstat(), "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        )
        for name in sorted(files):
            path = parent / name
            if (path.suffix in TEXT_SUFFIXES or path.name in {"LICENSE", "NOTICE", "COPYING"}
                    or (not path.suffix and parent.name == "bin")):
                result.append(path)
    return result


def evidence_category(value: object) -> str | None:
    """Recognize data envelopes, not their validity, decision or independence."""
    if not isinstance(value, dict) or value.get("schema_version") != 2:
        return None
    if value.get("artifact_kind") in {"swarm-report", "swarm-review"}:
        if {"work_map", "package_id", "leaf_ids", "attempt_id", "acceptance_digest", "result_digest"} <= value.keys():
            return "swarm observation payload"
    if {"work", "snapshot", "profile", "attempt_id", "builder", "qa_requirements"} <= value.keys():
        return "content-bound review context"
    if {"skill", "status", "timestamp", "context", "reviewer", "provenance", "controls",
        "coverage", "evidence"} <= value.keys():
        return "content-bound review decision"
    if {"context_digest", "controls", "evidence"} <= value.keys():
        return "bound QA observation"
    return None


def routing_lines(text: str, relative: str, exemptions: list[dict]) -> list[str]:
    lines = text.splitlines()
    if relative.endswith(".json"):
        try:
            category = evidence_category(json.loads(text))
        except json.JSONDecodeError:
            category = None
        if category:
            exemptions.append({"path": relative, "field": "$", "category": category,
                               "reason": "Recorded evidence data; only the shared contract can validate its binding, status or independence."})
            return []
    start = None
    for index, line in enumerate(lines):
        if line.strip() == "<!-- lintel-swarm-evidence:v2":
            start = index
        elif start is not None and line.strip() == "-->":
            try:
                category = evidence_category(json.loads("\n".join(lines[start + 1:index])))
            except json.JSONDecodeError:
                category = None
            if category:
                exemptions.append({"path": relative, "field": "lintel-swarm-evidence:v2",
                                   "line": start + 1, "end_line": index + 1, "category": category,
                                   "reason": "Recorded observation payload; its presence proves no binding or clearance, and surrounding narrative remains checked."})
                lines[start:index + 1] = [""] * (index + 1 - start)
            start = None
    return lines


def scan(root: Path, check: str = "all", exemptions: list[dict] | None = None) -> list[Finding]:
    root = root.resolve()
    if exemptions is None:
        exemptions = []
    findings: set[Finding] = set()

    def add(path: str, line: int, code: str, message: str) -> None:
        findings.add(Finding(path, line, code, message))

    names = set()
    skill_files = sorted((root / "skills").glob("*/SKILL.md"))
    if not skill_files:
        add("skills", 1, "missing-skill-tree", "No canonical SKILL.md files found.")
    for path in skill_files:
        relative = path.relative_to(root).as_posix()
        if any(part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 0x400
               for part in (path, path.parent, path.parent.parent)):
            add(relative, 1, "linked-path", "Refusing to read a linked workflow source.")
            continue
        header = frontmatter(path.read_text(encoding="utf-8-sig"))
        values = [line.partition(":")[2].strip(" \t'\"") for line in header
                  if line.startswith("name:")]
        if (len(values) != 1 or not re.fullmatch(NAME, values[0])
                or values[0].startswith("li-") or values[0] != path.parent.name):
            add(relative, 1, "invalid-name", "Canonical name must match its bare skill folder.")
        else:
            names.add(values[0])
        if check != "names":
            if path.parent.name.casefold() in RETIRED_COMMANDS:
                add(relative, 1, "retired-entry", "Retired canonical workflow is still discoverable.")
            for line, alias in declared_aliases(header):
                identity = alias.removeprefix("li-").casefold()
                if identity in RETIRED_COMMANDS:
                    add(relative, line, "retired-alias", f"Retired alias is still declared: {alias}")
    if check == "names":
        return sorted(findings)

    def command(relative: str, line: int, name: str, fixture_literal: bool = False) -> None:
        if name.casefold() in RETIRED_COMMANDS:
            add(relative, line, "retired-command", f"Retired workflow reference: {name}")
        elif name == "generate-X":
            exemptions.append({"path": relative, "line": line, "field": "format placeholder: generate-X",
                               "category": "documented template",
                               "reason": "Uppercase X denotes a format slot, not a callable workflow."})
        elif name not in names:
            if fixture_literal:
                exemptions.append({"path": relative, "line": line, "field": f"test literal: {name}",
                                   "category": "synthetic identity",
                                   "reason": "An unknown identity in test code is not a current workflow declaration; retired identities still fail."})
            else:
                add(relative, line, "missing-command", f"No canonical workflow for: {name}")

    for path in source_files(root):
        relative = path.relative_to(root).as_posix()
        if relative in SOURCE_EXCEPTIONS:
            exemptions.append({"path": relative, "field": "$file", "category": "declared source exception",
                               "reason": SOURCE_EXCEPTIONS[relative]})
            continue
        if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
            add(relative, 1, "linked-path", "Refusing to read a linked source file.")
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as error:
            add(relative, 1, "read-error", f"Cannot inspect text: {type(error).__name__}")
            continue
        if path.name == "SKILL.md" and path.parent.name.startswith("li-"):
            if path.parent.name[3:].casefold() in RETIRED_COMMANDS:
                add(relative, 1, "retired-entry", "Retired native wrapper is still discoverable.")
        test_code = relative.startswith("tests/") and path.suffix in {".py", ".sh", ".ps1"}
        former_column = False
        for number, original in enumerate(routing_lines(text, relative, exemptions), 1):
            line = URL.sub("", original).replace("\\|", "\x00").replace("\\", "/")
            if line.lstrip().startswith("|"):
                columns = line.split("|")
                first = columns[1].strip().casefold()
                if first in FORMER_HEADERS:
                    former_column = True
                if former_column:
                    if first and first not in FORMER_HEADERS and not re.fullmatch(r"[- :]+", first):
                        exemptions.append({"path": relative, "line": number, "field": "migration table, former-entry column",
                                           "category": "retired-name mapping",
                                           "reason": "The replacement column and all prose remain checked."})
                    line = "|" + " " * len(columns[1]) + "|" + "|".join(columns[2:])
            else:
                former_column = False
            for match in EXPLICIT_COMMAND.finditer(line):
                command(relative, number, match["name"], fixture_literal=test_code)
            for match in NATIVE_COMMAND.finditer(line):
                name = match["name"]
                # Bare li-* names can also be utilities or downstream examples.
                # Validate unknown workflows only in an explicit workflow namespace.
                if name.casefold() in RETIRED_COMMANDS:
                    utilities = [root / "bin" / ("li-" + name + suffix)
                                 for suffix in ("", ".py", ".sh", ".ps1")]
                    if any(item.is_file() for item in utilities):
                        exemptions.append({"path": relative, "line": number,
                                           "field": match[0], "category": "existing utility",
                                           "reason": "A bare utility name/message resolves in bin; explicit workflow invocations remain checked."})
                    else:
                        command(relative, number, name)
            for match in BARE_COMMAND.finditer(line):
                name = match["name"].casefold()
                action = re.search(r"\b(?:run|invoke|use|command|workflow|skill)\b",
                                   line[:match.start()], re.I)
                if action and name in RETIRED_COMMANDS and name not in HOST_SLASH_COMMANDS:
                    command(relative, number, name)
            for match in NAMED_SKILL.finditer(line):
                name = match["before"] or match["after"]
                if name.casefold() in RETIRED_COMMANDS:
                    command(relative, number, name)
            for match in SKILL_FIELD.finditer(line):
                if (path.suffix == ".py" and re.search(r"\bskill\s*:\s*" + re.escape(match["name"]) + r"\b", match[0])
                        and not re.search(r"""[:=]\s*["']""", match[0])):
                    exemptions.append({"path": relative, "line": number,
                                       "field": match[0].strip(), "category": "Python annotation",
                                       "reason": "An unquoted Python type annotation is not a literal workflow identity."})
                    continue
                command(relative, number, match["name"], fixture_literal=test_code)
            if (path.suffix in {".md", ".template"}
                    or (path.suffix in {".json", ".yaml", ".yml", ".toml"}
                        and re.search(r"\b(?:description|workflow|skill|method)\b", line, re.I))):
                for match in DISTINCTIVE_COMMAND.finditer(line):
                    command(relative, number, match[1])
            links = list(LINK.finditer(line))
            for match in SKILL_PATH.finditer(line):
                if line[match.end():match.end() + 1] in {"*", "$", "<", "{"}:
                    continue
                name = match["name"]
                identity = name.removeprefix("li:").removeprefix("li-") if match["prefix"] != "skills/" else name.removeprefix("li:")
                if identity.casefold() in RETIRED_COMMANDS:
                    command(relative, number, identity)
                if any(link.start(1) <= match.start() < link.end(1) for link in links):
                    continue
                if not match["tail"] and identity not in names and identity not in RETIRED_COMMANDS:
                    continue
                target = unquote(match[0].rstrip("."))
                if not Path(target).suffix and identity not in names and identity not in RETIRED_COMMANDS:
                    continue  # Prose such as skills/agents/hooks is a list, not a workflow path.
                if not match["tail"]:
                    target += "/SKILL.md"
                if test_code and not re.search(r"\b(?:ROOT|REPO_ROOT|SOURCE_ROOT)\b", line[:match.start()]):
                    exemptions.append({"path": relative, "line": number, "field": f"test path literal: {target}",
                                       "category": "fixture-relative path",
                                       "reason": "No literal source-root consumer on this line; fixture paths need not exist in the source tree. Retired identities still fail."})
                    continue
                if not (root / target).exists():
                    if (test_code and path.suffix == ".py"
                            and re.search(r"\bself\.assertFalse\s*\(", line[:match.start()])
                            and re.search(r"\.exists\(\)\s*\)", line[match.end():])):
                        exemptions.append({"path": relative, "line": number,
                                           "field": target, "category": "negative absence assertion",
                                           "reason": "This assertion requires the resource to remain absent; positive imports/selections still require it."})
                    else:
                        add(relative, number, "missing-path", f"Unresolved workflow path: {target}")
            if path.suffix in {".md", ".template"}:
                for match in links:
                    target = unquote(match[1].strip("<>").split("#", 1)[0])
                    if (not target or re.match(r"[a-z]+:", target, re.I) or target.startswith("/")
                            or any(token in target for token in ("<", ">", "$", "{", "*"))):
                        continue
                    resolved = (path.parent / target).resolve()
                    if resolved.is_relative_to(root) and not resolved.exists():
                        add(relative, number, "missing-path", f"Unresolved local link: {target}")
    return sorted(findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--check", choices=("all", "names"), default="all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    exemptions: list[dict] = []
    try:
        findings = scan(args.root, args.check, exemptions)
    except (OSError, ValueError) as error:
        parser.exit(2, f"ERROR: command-surface check failed: {error}\n")
    if args.json:
        print(json.dumps({"ok": not findings, "findings": [asdict(item) for item in findings],
                          "exemptions": exemptions}, indent=2))
    else:
        for item in findings:
            print(f"{item.path}:{item.line}: {item.code}: {item.message}")
        for item in exemptions:
            print(f"EXEMPT {item['path']} [{item['field']}]: {item['reason']}")
        print(f"native-command-surface: {'FAIL' if findings else 'PASS'} ({len(findings)} findings)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
