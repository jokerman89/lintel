#!/usr/bin/env python3
# component: agent-inventory-tests
# implements: ADR-0028, ADR-0039
# intent: .claude/plans/v2-findings/plan.md
# constraints: derived source inventories and in-memory rendering only; no activation or portfolio extraction
# last_intent_review: 2026-10-03
"""Inventory/member/catalog/native parity, without a role or neutral-category floor."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ".claude/engineering/audits/2026-09-20-universal-quality/agents-inventory.md"
PRESERVATION = ".claude/plans/universal-implementation/reports/P09-agent-preservation.md"


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


catalog = load("inventory_catalog", "bin/li-catalog.py")
adapter = load("inventory_native", "bin/li-copilot.py")
HOST = adapter.NATIVE_HOSTS["copilot"]


def named_rows(text):
    return re.findall(r"^\| \[([A-Za-z0-9]+)\]\(", text, re.MULTILINE)


def unique(values, label):
    if len(values) != len({value.casefold() for value in values}):
        raise AssertionError(f"{label}: duplicate identity")
    return set(values)


def validate(canonical, entries, native, referenced, original, preserved):
    """Test oracle over derived inventories; not a new production registry."""
    names = unique([item["name"] for item in canonical], "canonical")
    assert names, "canonical inventory is empty"
    unique([item["path"] for item in canonical], "canonical paths")
    for item in canonical:
        path = Path(item["path"])
        assert path.stem == item["name"], "canonical name/file mismatch"
        assert path.parent.name == item["category"], "canonical category/directory mismatch"
        assert item["tools"], "canonical tools missing"
    unique([item["name"] for item in entries], "catalog")
    expected_catalog = {(item["name"], item["path"], item["category"]) for item in canonical}
    assert expected_catalog == {(item["name"], item["path"], item["category"]) for item in entries}, \
        "catalog inventory drift"
    assert set(referenced) <= {"agent:" + name for name in names}, "unknown referenced member"
    originals = unique(original, "original inventory")
    assert originals and originals <= names, "an original public name disappeared"
    assert unique(preserved, "preservation") == originals, "preservation rows drift"
    expected_native = {
        f".github/agents/{name}.agent.md" for name in names
    } | {f".github/agents/lintel-{role}.agent.md" for role in adapter.AGENTS}
    assert set(native) == expected_native, "native inventory drift"
    for item in canonical:
        path = f".github/agents/{item['name']}.agent.md"
        header, _ = adapter.split_frontmatter(native[path].decode("utf-8"))
        assert adapter.frontmatter_value(header, "name", path) == item["name"], "native name drift"
        assert adapter.frontmatter_value(header, "tools", path) == item["tools"], "native tools drift"
    return {"canonical": len(names), "catalog": len(entries),
            "native_canonical": len(native) - len(adapter.AGENTS),
            "native_orchestration": len(adapter.AGENTS), "original_preserved": len(originals),
            "unique_referenced_agents": len(set(referenced)),
            "categories": sorted({item["category"] for item in canonical})}


class AgentInventory(unittest.TestCase):
    def fixture(self):
        # Two roles in a non-neutral category must pass: validity, not size, is the guard.
        canonical = [{"name": name, "path": f"agents/experimental/{name}.md",
                      "category": "experimental", "tools": "Read, Grep"}
                     for name in ("One", "Two")]
        entries = copy.deepcopy(canonical)
        native = {f".github/agents/{item['name']}.agent.md": (
            f"---\nname: {item['name']}\ndescription: Fixture\ntools: {item['tools']}\n---\n"
        ).encode() for item in canonical}
        native.update({f".github/agents/lintel-{role}.agent.md": b"fixture role\n"
                       for role in adapter.AGENTS})
        return [canonical, entries, native, ["agent:One"], ["One", "Two"], ["One", "Two"]]

    def test_small_non_neutral_inventory_passes(self):
        result = validate(*self.fixture())
        self.assertEqual(result["canonical"], 2)
        self.assertEqual(result["categories"], ["experimental"])

    def test_duplicate_names_case_collisions_and_misplaced_categories_fail(self):
        for field, value in (("name", "one"), ("category", "another"), ("path", "agents/experimental/Other.md")):
            args = self.fixture()
            args[0][1][field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                validate(*args)

    def test_dangling_member_and_catalog_drift_fail(self):
        args = self.fixture()
        args[3].append("agent:Missing")
        with self.assertRaisesRegex(AssertionError, "referenced"):
            validate(*args)
        for mutation in ("missing", "path", "duplicate"):
            args = self.fixture()
            if mutation == "missing":
                args[1].pop()
            elif mutation == "path":
                args[1][0]["path"] = "agents/elsewhere/One.md"
            else:
                args[1].append(copy.deepcopy(args[1][0]))
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                validate(*args)

    def test_native_missing_extra_or_changed_tools_fail(self):
        for mutation in ("missing", "extra", "tools"):
            args = self.fixture()
            path = ".github/agents/One.agent.md"
            if mutation == "missing":
                del args[2][path]
            elif mutation == "extra":
                args[2][".github/agents/Unregistered.agent.md"] = b"unexpected"
            else:
                args[2][path] = args[2][path].replace(b"Read, Grep", b"Read, Write")
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                validate(*args)

    def test_original_name_cannot_disappear_even_if_live_views_agree(self):
        args = self.fixture()
        args[0].pop()
        args[1].pop()
        del args[2][".github/agents/Two.agent.md"]
        with self.assertRaisesRegex(AssertionError, "original public name"):
            validate(*args)
        args = self.fixture()
        args[5].append("One")
        with self.assertRaisesRegex(AssertionError, "preservation"):
            validate(*args)

    def test_real_source_catalog_members_and_native_rendering_agree(self):
        canonical = []
        for path in sorted((ROOT / "agents").glob("*/*.md")):
            if path.name == "README.md" or path.name.startswith("_"):
                continue
            header = catalog.frontmatter(path)
            canonical.append({
                "name": catalog.scalar(header, "name", path),
                "path": path.relative_to(ROOT).as_posix(),
                "category": catalog.scalar(header, "category", path),
                "tools": catalog.scalar(header, "tools", path),
            })
        metadata = catalog.metadata(ROOT, kind="all")
        self.assertFalse(metadata["executed"])
        entries = [item for item in metadata["entries"] if item["kind"] == "agent"]
        # Use the existing registry validator: no competing selection parser or registry.
        data, _, _ = catalog.selection_data(ROOT, metadata["entries"])
        selections = data["selections"]
        referenced = [member for record in selections.values() for member in record["members"]
                      if member.startswith("agent:")]
        # Render in memory only; do not write .github or claim live host acceptance.
        rendered = adapter.native_files(ROOT, {}, True, HOST)
        native = {path: value for path, value in rendered.items() if path.startswith(".github/agents/")}
        original = named_rows((ROOT / INVENTORY).read_text(encoding="utf-8"))
        preserved = named_rows((ROOT / PRESERVATION).read_text(encoding="utf-8"))
        result = validate(canonical, entries, native, referenced, original, preserved)
        print("SOURCE INVENTORY PARITY " + json.dumps(result, sort_keys=True), flush=True)

    def test_shell_entry_uses_parity_not_a_fixed_floor(self):
        text = (ROOT / "tests/unit/agents-categorized.sh").read_text(encoding="utf-8")
        self.assertIn("agent-inventory.py", text)
        self.assertNotIn("EXPECTED_CATEGORIES", text)
        self.assertNotIn("-ge 60", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
