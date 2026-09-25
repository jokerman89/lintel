#!/usr/bin/env bash
# component: event-catalog-producers-test
# implements: ADR-0008
# intent: .claude/plans/universal-implementation/packages/P08.md
# constraints: static extraction of code producers only; instruction-only producers are exempt from call extraction
# last_intent_review: 2026-09-23
# Asserts lib/event-catalog.json covers every audit_log and declared wrapper call
# under bin/, lib/ and hooks/ (continuation lines included): literal producers are
# catalogued, non-literal calls match a dynamic entry, every catalogued code
# producer still exists, and every hooks/shared/ hook is either a producer or a
# declared non-recording hook. Field order is left to the round-trip tests.
# tag: shape observation catalog
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "tests/shape/event-catalog-producers.sh"
echo "======================================"

python="${LINTEL_PYTHON:-python3}"
if ! "$python" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
  python=python
fi
if ! "$python" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
  echo '  SKIP: Python 3.9+ required for catalog coverage extraction'
  exit 0
fi

FAILED=0
if [ ! -f "$REPO_ROOT/lib/event-catalog.json" ]; then
  echo "  FAIL: lib/event-catalog.json missing"
  exit 1
fi
rc=0
PYTHONDONTWRITEBYTECODE=1 "$python" "$REPO_ROOT/bin/li-events.py" summary \
  --file "$REPO_ROOT/.claude/runtime/catalog-shape-absent.jsonl" >/dev/null 2>&1 || rc=$?
if [ "$rc" = 3 ]; then
  echo "  PASS: the structured reader loads and validates the catalog"
else
  echo "  FAIL: the structured reader rejected the catalog (exit $rc)"
  FAILED=1
fi

PYTHONDONTWRITEBYTECODE=1 "$python" - "$REPO_ROOT" <<'PY' || FAILED=1
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
catalog = json.loads((root / "lib/event-catalog.json").read_text(encoding="utf-8"))
failures = []


def fail(message):
    failures.append(message)
    print("  FAIL: " + message)


wrappers = {entry["name"] for entry in catalog.get("wrappers", [])}
names = {"audit_log"} | wrappers
CALL = re.compile(r"(?<![\w-])(" + "|".join(sorted(map(re.escape, names))) + r")(?![\w-])")
PREFIX_OK = re.compile(r"(^|;|&&|\|\||\||\(|\{|\)|\bthen|\bdo|\belse|!)\s*$")
ASSIGNMENTS = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*=(\"[^\"]*\"|'[^']*'|\S*)\s+)+$")


def skip_quoted(text, i, quote):
    while i < len(text):
        if quote == '"' and text[i] == "\\":
            i += 2
            continue
        if text[i] == quote:
            return i + 1
        i += 1
    raise ValueError("unterminated quote")


def skip_group(text, i, opening, closing):
    depth = 1
    while i < len(text):
        c = text[i]
        if c in "'\"":
            i = skip_quoted(text, i + 1, c)
            continue
        if c == "\\":
            i += 2
            continue
        if c == opening:
            depth += 1
        elif c == closing:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unterminated group")


def dollar(text, i):
    if text.startswith("$((", i):
        return skip_group(text, i + 3, "(", ")") + 1
    if text.startswith("$(", i):
        return skip_group(text, i + 2, "(", ")")
    if text.startswith("${", i):
        return skip_group(text, i + 2, "{", "}")
    match = re.match(r"\$([A-Za-z_][A-Za-z0-9_]*|[@*#?$!0-9-])", text[i:])
    return i + (match.end() if match else 1)


def words(text, i):
    """Shell words after a call name, up to the first unquoted command terminator."""
    result, word = [], None
    while i < len(text):
        c = text[i]
        if c == "\\" and text.startswith("\\\n", i):
            i += 2
            continue
        if c in " \t":
            if word is not None:
                result.append(word)
                word = None
            i += 1
            continue
        if c in "\n;&|<>)" or (c == "#" and word is None) or (
                c.isdigit() and word is None and text[i + 1:i + 2] in ("<", ">")):
            break
        word = word if word is not None else []
        if c == "'":
            end = skip_quoted(text, i + 1, "'")
            word.append(("lit", text[i + 1:end - 1]))
            i = end
        elif c == '"':
            i += 1
            while text[i] != '"':
                if text[i] == "\\":
                    word.append(("lit", text[i + 1]))
                    i += 2
                elif text[i] == "$":
                    end = dollar(text, i)
                    word.append(("var", text[i:end]))
                    i = end
                elif text[i] == "`":
                    end = skip_quoted(text, i + 1, "`")
                    word.append(("var", text[i:end]))
                    i = end
                else:
                    word.append(("lit", text[i]))
                    i += 1
            i += 1
        elif c == "$":
            end = dollar(text, i)
            word.append(("var", text[i:end]))
            i = end
        else:
            word.append(("lit", c))
            i += 1
    if word is not None:
        result.append(word)
    return result


def literal(word):
    return "".join(t for kind, t in word) if all(kind == "lit" for kind, t in word) else None


def pattern(word):
    return "^" + "".join(re.escape(t) if kind == "lit" else ".+" for kind, t in word) + "$"


def field_key(word):
    text = ""
    for kind, t in word:
        if kind != "lit":
            return None
        text += t
        if "=" in text:
            key = text.split("=", 1)[0]
            return key if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) else None
    return None


def functions(lines, python):
    spans = []
    for number, line in enumerate(lines):
        if python:
            match = re.match(r"^(\s*)def\s+(\w+)\s*\(", line)
            if not match:
                continue
            indent, end = len(match.group(1)), len(lines)
            for later in range(number + 1, len(lines)):
                stripped = lines[later].strip()
                if stripped and len(lines[later]) - len(lines[later].lstrip()) <= indent:
                    end = later
                    break
            spans.append((number, end, match.group(2)))
            continue
        match = re.match(r"^(\s*)(?:function\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*([{(])?(.*)$", line)
        if not match:
            continue
        indent, opener, rest = match.group(1), match.group(3), match.group(4).rstrip()
        closer = {"{": "}", "(": ")"}.get(opener or "{", "}")
        if opener and rest.endswith(closer):
            spans.append((number, number + 1, match.group(2)))
            continue
        end = len(lines)
        for later in range(number + 1, len(lines)):
            if re.fullmatch(re.escape(indent) + r"[})]\s*", lines[later]):
                end = later + 1
                break
        spans.append((number, end, match.group(2)))
    return spans


def producer_for(rel, lines, spans, line_number):
    hook = re.fullmatch(r"hooks/shared/([^/]+)/run\.sh", rel)
    if hook:
        return "hook:" + hook.group(1)
    inside = [name for start, end, name in spans if start <= line_number < end]
    return f"{rel}:{inside[-1]}" if inside else rel


def is_script(path):
    if path.suffix in (".sh", ".py"):
        return True
    if path.suffix:
        return False
    try:
        first = path.open("rb").readline().decode("utf-8", "replace").strip()
    except OSError:
        return False
    return first.startswith("#!") and ("sh" in first or "python" in first)


calls = []
for folder in ("bin", "lib", "hooks"):
    for path in sorted((root / folder).rglob("*")):
        if not path.is_file() or not is_script(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        if not CALL.search(text):
            continue
        rel = path.relative_to(root).as_posix()
        lines = text.split("\n")
        spans = functions(lines, path.suffix == ".py")
        offsets, total = [], 0
        for line in lines:
            offsets.append(total)
            total += len(line) + 1
        for match in CALL.finditer(text):
            line_number = text.count("\n", 0, match.start())
            before = text[offsets[line_number]:match.start()]
            if before.lstrip().startswith("#") or text.startswith("()", match.end()) or \
                    re.match(r"\s*\(\)", text[match.end():]):
                continue
            if not (PREFIX_OK.search(before) or ASSIGNMENTS.match(before)):
                continue
            try:
                parsed = words(text, match.end())
            except (ValueError, IndexError) as exc:
                fail(f"{rel}:{line_number + 1}: cannot parse {match.group(1)} call ({exc})")
                continue
            calls.append({"rel": rel, "line": line_number + 1, "name": match.group(1), "words": parsed,
                          "producer": producer_for(rel, lines, spans, line_number), "lines": lines,
                          "spans": spans})

categories = catalog["categories"]
dynamic = catalog.get("dynamic", [])
produced = {}
print(f"  PASS: extracted {len(calls)} producer calls from bin/, lib/ and hooks/")
for call in calls:
    where = f"{call['rel']}:{call['line']}"
    if len(call["words"]) < 1:
        fail(f"{where}: call without a category")
        continue
    category_word = call["words"][0]
    category = literal(category_word)
    # audit_log defaults a missing kind to "event"; a forwarding "$@" carries its kind.
    kind_word = call["words"][1] if len(call["words"]) > 1 else (
        [("lit", "event")] if category is not None else [("var", "$@")])
    field_words = call["words"][2:]
    kind = literal(kind_word)
    keys = [field_key(word) for word in field_words]
    if category is not None and kind is not None and None not in keys:
        entry = categories.get(category, {}).get("kinds", {}).get(kind)
        if entry is None:
            fail(f"{where}: literal producer {category}/{kind} missing from the catalog")
            continue
        if call["producer"] not in entry["producers"]:
            fail(f"{where}: catalog does not list {call['producer']} for {category}/{kind}")
        for key in keys:
            if key not in entry["fields"]:
                fail(f"{where}: field {key} of {category}/{kind} is not catalogued")
        produced.setdefault(call["producer"], set()).add((category, kind))
        continue
    matches = []
    for item in dynamic:
        if item["call_site"] != call["producer"]:
            continue
        if category is not None and category != item.get("category") and not (
                item.get("category_pattern") and re.fullmatch(item["category_pattern"], category)):
            continue
        if category is None and not item.get("category_pattern"):
            continue
        if kind is not None and not re.fullmatch(item["kind_pattern"], kind):
            continue
        if kind is None and not item.get("wrapper") and not all(
                re.fullmatch(pattern(kind_word), known) for known in item.get("kinds", [])):
            continue
        if None in keys and not item.get("fields_dynamic"):
            continue
        if any(key is not None and key not in item.get("fields", []) for key in keys):
            continue
        matches.append(item)
    if not matches:
        fail(f"{where}: non-literal {call['name']} call does not match a dynamic entry")
        continue
    for item in matches:
        for known in item.get("kinds", []):
            produced.setdefault(call["producer"], set()).add((item["category"], known))
        if item.get("delegated_kinds"):
            produced.setdefault(call["producer"], set()).add((item["category"], "*"))

source_calls = {}
for call in calls:
    source_calls.setdefault(call["rel"], set()).add(call["producer"])


def defined(rel, function):
    path = root / rel
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return re.search(r"(?m)^\s*(?:function\s+|def\s+)?" + re.escape(function) + r"\s*\(", text) is not None


hook_producers = set()
for category, meta in categories.items():
    listed = meta.get("producers", []) if meta.get("delegated") else []
    for producer in listed:
        if (category, "*") not in produced.get(producer, set()):
            fail(f"delegated {category} producer {producer} no longer writes the category")
    for kind, entry in meta.get("kinds", {}).items():
        for producer in entry["producers"]:
            if producer.startswith("instruction-only:"):
                skill = root / producer.split(":", 1)[1]
                text = skill.read_text(encoding="utf-8") if skill.is_file() else ""
                if category not in text or kind not in text:
                    fail(f"instruction-only producer {producer} does not name {category}/{kind}")
                continue
            if producer.startswith("hook:"):
                hook = producer.split(":", 1)[1]
                hook_producers.add(hook)
                run = root / "hooks/shared" / hook / "run.sh"
                if not run.is_file():
                    fail(f"catalog producer {producer} no longer exists")
                    continue
                if (category, kind) in produced.get(producer, set()):
                    continue
                body = run.read_text(encoding="utf-8", errors="replace")
                via = [other for other in entry["producers"] if ":" in other and not other.startswith(
                    ("hook:", "instruction-only:")) and re.search(
                        r"(?<![\w-])" + re.escape(other.rsplit(":", 1)[1]) + r"(?![\w-])", body)]
                if not via:
                    fail(f"catalog producer {producer} no longer produces {category}/{kind}")
                continue
            rel, _, function = producer.partition(":")
            if not (root / rel).is_file() or (function and not defined(rel, function)):
                fail(f"catalog producer {producer} no longer exists")
            elif (category, kind) not in produced.get(producer, set()):
                fail(f"catalog producer {producer} no longer produces {category}/{kind}")

for item in dynamic:
    rel, _, function = item["call_site"].partition(":")
    if not (root / rel).is_file() or (function and not defined(rel, function)):
        fail(f"dynamic call site {item['call_site']} no longer exists")
    for known in item.get("kinds", []):
        if known not in categories.get(item.get("category", ""), {}).get("kinds", {}):
            fail(f"dynamic entry {item['call_site']} names uncatalogued kind {known}")

hooks_on_disk = {path.parent.name for path in (root / "hooks/shared").glob("*/run.sh")}
silent = {}
for entry in catalog.get("non_recording_hooks", []):
    if not entry.get("reason"):
        fail(f"non-recording hook {entry.get('hook')} has no reason")
    silent[entry["hook"]] = entry
for hook in sorted(hooks_on_disk):
    if hook in hook_producers and hook in silent:
        fail(f"hook {hook} is both a catalog producer and non-recording")
    elif hook not in hook_producers and hook not in silent:
        fail(f"hook directory {hook} is neither a catalog producer nor in non_recording_hooks")
for hook in sorted(set(silent) - hooks_on_disk):
    fail(f"non-recording hook {hook} no longer exists")
for hook in sorted(silent):
    if f"hook:{hook}" in produced:
        fail(f"non-recording hook {hook} contains a producer call")

if failures:
    sys.exit(1)
print(f"  PASS: every producer call is catalogued; {len(hooks_on_disk)} hook directories accounted for")
PY

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All event-catalog-producers assertions PASSED"; exit 0
else echo "Some event-catalog-producers assertions FAILED"; exit 1; fi
