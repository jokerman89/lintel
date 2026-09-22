#!/usr/bin/env python3
# component: document-format-pipeline-tests
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: synthetic local fixtures; OOXML retention is not rendered-layout acceptance
# last_intent_review: 2026-09-22
"""Check the standalone document instructions, accepted controls, and explicit artifacts."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


TITLE = "Synthetic queue checkpoint design"
SECTIONS = (
    ("Decision and scope", (
        "This brief evaluates a synthetic queue worker that acknowledges an item only after "
        "recording its completion in a durable checkpoint. All identifiers, workloads, timings, "
        "and evidence files in this exercise are invented test material. They describe a "
        "deterministic analytical model, not a measured service, customer workload, or production "
        "benchmark. The decision is to separate processing completion from acknowledgement "
        "eligibility, and to retain enough state to explain a retry. A shorter presentation may "
        "emphasize that decision, but it must not remove the assumptions that limit it. "
        "The editable document is the full technical argument; the deck is a presentation view "
        "with the complete argument in its actual speaker notes. [S1]",
        "The acceptance question is deliberately narrower than whether the queue is reliable "
        "in every environment. It asks whether a consumer can distinguish an unprocessed item, "
        "a completed item with an unconfirmed checkpoint, and an acknowledged item in this "
        "specific model. Those states lead to different recovery decisions. Combining them into "
        "one success flag would hide the interval in which duplicate delivery is expected. "
        "The proposal therefore records the item identifier and completion outcome before "
        "emitting an acknowledgement, and treats uncertain persistence as a retry condition "
        "rather than proof of success. That ordering is necessary for the argument below, "
        "but it is not sufficient to prove an external side effect happened only once. [S2]",
    )),
    ("Reasoning across the checkpoint boundary", (
        "Consider an item whose external operation completes and whose local checkpoint write "
        "has not yet returned. If the worker stops at that point, a replacement cannot infer "
        "durability from the fact that the first worker performed useful work. It must consult "
        "the checkpoint or retry according to the consumer's documented idempotency contract. "
        "This is why an acknowledgement cannot be emitted merely when the handler returns. "
        "The handler's return describes one computation, while the acknowledgement changes "
        "delivery responsibility. The two events belong to different failure boundaries. "
        "Keeping both events explicit preserves the distinction when an operator investigates "
        "a duplicate, rather than making the duplicate look like contradictory evidence. [S2]",
        "Now consider the converse interruption: the checkpoint becomes durable, but the "
        "acknowledgement is lost. A redelivery can look up the stored completion outcome and "
        "avoid repeating an operation only if the identifier remains stable and the stored "
        "record covers the same input version. Reusing an identifier for changed input would "
        "invalidate that inference. The design therefore compares both identifier and input "
        "version before reuse, and records a conflict instead of silently accepting a stale "
        "result. Retention of checkpoint records must cover the stated redelivery interval. "
        "Expiring them earlier changes the guarantee and belongs in the operational contract, "
        "not in a footnote removed to meet a slide word limit. [S2]",
    )),
    ("Analytical capacity and evidence", (
        "The capacity table uses a deliberately simple calculation. One worker performs one "
        "modeled service step every 100 milliseconds, so its ideal upper bound is ten items "
        "per second. Two independent workers have an ideal bound of twenty, and four have "
        "an ideal bound of forty. These are arithmetic consequences of the assumptions, "
        "not observations from a load test. The model excludes checkpoint latency, contention, "
        "network delay, scheduling overhead, retries, and queue imbalance. The word ideal is "
        "therefore part of each capacity claim. Removing it would turn a scoped analytical "
        "result into an unsupported performance promise. The table keeps units and the "
        "excluded costs beside the values so that a reader can audit the calculation. [S1]",
        "The claim ledger separates what follows from the model from what still needs evidence. "
        "C1 follows from the service-step arithmetic in S1. C2 follows only from the event "
        "ordering and stable input identity in S2; it does not assert exactly-once execution "
        "of an external operation. C3 records that storage failure behavior has not been "
        "tested here. This negative claim is material to the decision, not optional prose. "
        "Adding several minor warnings would not compensate for omitting it. A future test "
        "must record the exact storage implementation, interruption points, recovery procedure, "
        "and observed results before the argument can be extended beyond its current "
        "analytical boundary. Until then the untested part remains explicitly unverified. [S2]",
    )),
    ("Material limitation and recovery", (
        "MATERIAL LIMITATION: this synthetic exercise does not test power loss during a storage "
        "flush, a damaged checkpoint, or a service that ignores the idempotency identifier. "
        "A handler may already have changed that external service before a worker learns "
        "that its checkpoint could not be confirmed. Retrying can then repeat the external "
        "side effect. The document must not call this exactly-once processing or claim that "
        "a valid checkpoint file eliminates that risk. The proposed mitigation is a "
        "service-supported idempotency key with a versioned request and a retention interval "
        "aligned to redelivery, followed by an actual failure-injection experiment. None of "
        "those experiments is reported as executed in this brief. [S2]",
        "Recovery starts by preserving the ambiguous record and its input version, not by "
        "deleting it until the dashboard becomes green. An operator compares the external "
        "service's response evidence with the checkpoint state, classifies the result as "
        "confirmed, rejected, or unknown, and chooses the next permitted action. Unknown "
        "is a useful outcome because it prevents a false acknowledgement while information "
        "is incomplete. The same principle applies to this artifact pipeline: missing "
        "rendered inspection is not a passing layout check, and a successful file reopen "
        "does not prove every page or slide was visible without clipping. Each observation "
        "must name the layer actually inspected and retain the unresolved boundary. [S2]",
    )),
    ("Validation and decision follow-up", (
        "The next engineering experiment would exercise interruptions before the handler, "
        "after the external response, during checkpoint persistence, and after persistence "
        "but before acknowledgement. It would check identifier reuse with changed input, "
        "checkpoint expiry before redelivery, and the reconciliation path for an unknown "
        "external result. Those are proposed checks, not a list of passing tests. A result "
        "record should include the exact input, implementation version, observed event "
        "order, and any missing observation. If one required observation cannot be collected, "
        "independent preparation can continue, but the corresponding guarantee cannot be "
        "promoted. This keeps the design useful without confusing a planned experiment "
        "with evidence that has already been obtained. [S2]",
        "For the document experiment, the full paragraphs, both source citations, capacity "
        "table, claim ledger, and material limitation must survive Word and slide composition. "
        "Word should keep editable paragraphs and table cells. The deck may use a short "
        "visible summary, but must place these complete arguments in real notes and retain "
        "the accompanying long-form source. Reopen each saved artifact through the available "
        "API, make a small reversible text edit, and read it back. Inspect rendered slides "
        "where an actual renderer exists. Record any unavailable page renderer explicitly. "
        "Neither a package-size check nor a count of warnings establishes fidelity, layout "
        "quality, independent review, or permission to distribute the result. [S1] [S2]",
    )),
)
CAPACITY = (
    ("Workers", "Service step (ms)", "Ideal items/s"),
    ("1", "100", "10"),
    ("2", "100", "20"),
    ("4", "100", "40"),
)
CLAIMS = (
    ("Claim", "Evidence", "Boundary"),
    ("C1: ideal capacity", "S1 arithmetic", "No measured throughput"),
    ("C2: checkpoint before acknowledgement", "S2 event model", "Not exactly-once side effects"),
    ("C3: storage failure is unverified", "S2 missing experiment", "Power-loss test still required"),
)
REFERENCES = (
    "[S1] sources/analytical-model.txt - synthetic arithmetic and explicit exclusions.",
    "[S2] sources/failure-model.txt - synthetic event ordering, assumptions, and untested failures.",
)
SOURCE_CLOSURE = (
    "bin/li-review-evidence.py", "lib/review_contract.py", "lib/review-schema.json",
    "lib/markdown_source.py", "lib/profile_context.py", "lib/profile-context-schema.json",
    "lib/native_paths.py", "lib/pack-schema.yaml", "packs/_default/pack.yaml",
    ".claude-plugin/plugin.json",
)
ROOT = Path(__file__).resolve().parents[2]
OPTIONS = None
RUN = None
RC = None
PC = None
CLI = None


def table_markdown(rows):
    return "\n".join(
        ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join("---" for _ in rows[0]) + " |"]
        + ["| " + " | ".join(row) + " |" for row in rows[1:]]
    )


def write_fixture(target: Path) -> None:
    """Author only the explicitly selected synthetic source, never Office bytes."""
    target.mkdir(parents=True, exist_ok=True)
    brief = "# " + TITLE + "\n\nLanguage: en-GB. Audience: engineers. All data is synthetic.\n"
    content = []
    for index, (title, paragraphs) in enumerate(SECTIONS, 1):
        body = "\n\n".join(paragraphs)
        brief += "\n## " + title + "\n\n" + body + "\n"
        content.append(
            f"## \u00a7{index} - {title} {{#sec-{index}}}\n\n"
            f"<!-- voice: null -->\n<!-- type: content -->\n"
            f"<!-- key_message: {title} -->\n\n**Title:** {title}\n\n**Body:**\n{body}\n"
        )
    tables = "\n\n### Capacity table\n\n" + table_markdown(CAPACITY)
    tables += "\n\n### Claim/evidence ledger\n\n" + table_markdown(CLAIMS)
    sources = "\n\n### Sources\n\n" + "\n\n".join(REFERENCES) + "\n"
    brief += tables + sources
    outline = (
        "---\ntitle: Synthetic queue checkpoint design\nlanguage: en-GB\n"
        "audience: engineers\narc: deep-dive\ntarget_formats: [word, ppt]\n"
        "slide_count_target: 6\nsource_brief_hash: "
        + hashlib.sha256(brief.encode()).hexdigest() + "\n---\n\n"
        + "\n".join(f"## \u00a7{i} - {title}\n- **source_material:** brief.md, {title}\n"
                    for i, (title, _) in enumerate(SECTIONS, 1))
    )
    written = (
        "---\ntitle: Synthetic queue checkpoint design\nlanguage: en-GB\n"
        "audience: engineers\narc: deep-dive\ntarget_formats: [word, ppt]\n"
        "voice_tier: internal\nsource_outline_hash: "
        + hashlib.sha256(outline.encode()).hexdigest() + "\n---\n\n# " + TITLE + "\n\n"
        + "\n".join(content) + tables + sources
    )
    notes = (
        "---\nlanguage: en-GB\nsource_content_hash: "
        + hashlib.sha256(written.encode()).hexdigest() + "\n---\n\n"
        + "\n".join(f"## \u00a7{i} - {title}\n\n" + "\n\n".join(paragraphs) + "\n"
                    for i, (title, paragraphs) in enumerate(SECTIONS, 1))
        + tables + sources
    )
    files = {
        "brief.md": brief, "outline.md": outline, "content.md": written,
        "speaker-notes.md": notes,
        "sources/analytical-model.txt": "S1: SYNTHETIC. Ideal capacity = workers * 1000 / 100 ms.\n"
        "1 -> 10, 2 -> 20, 4 -> 40 items/s. Excludes persistence, contention, network, scheduling, retries and imbalance.\n",
        "sources/failure-model.txt": "S2: SYNTHETIC. Handler -> confirmed checkpoint -> acknowledgement.\n"
        "Stable identifier and input version are assumptions. Power loss, damaged records and external idempotency are untested.\n",
    }
    for relative in files:
        if (target / relative).exists():
            raise FileExistsError(f"Refusing to replace fixture source: {relative}")
    for relative, text in files.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)


def document_text(path: Path) -> dict[str, str]:
    """Extract OOXML text for retention only; this does not render or open Office."""
    result = {}
    with ZipFile(path) as package:
        for name in package.namelist():
            if path.suffix == ".docx":
                selected = name == "word/document.xml"
            else:
                selected = bool(re.fullmatch(r"ppt/(slides/slide|notesSlides/notesSlide)\d+\.xml", name))
            if selected:
                root = ET.fromstring(package.read(name))
                result[name] = " ".join(node.text or "" for node in root.iter()
                                       if node.tag.rsplit("}", 1)[-1] == "t")
    if not result:
        raise ValueError("No document/slide text parts found")
    return result


def missing_content(parts: dict[str, str]) -> list[str]:
    text = " ".join(" ".join(parts.values()).split())
    required = [p for _, paragraphs in SECTIONS for p in paragraphs]
    required += list(REFERENCES)
    required += [cell for rows in (CAPACITY, CLAIMS) for row in rows for cell in row]
    return [part for part in required if " ".join(part.split()) not in text]


def slide_notes(path: Path) -> list[str]:
    """Follow the synthetic deck's real relationships, detecting native part aliasing."""
    notes = []
    targets = set()
    with ZipFile(path) as package:
        slides = sorted((name for name in package.namelist()
                         if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
                        key=lambda name: int(re.search(r"slide(\d+)", name).group(1)))
        for slide in slides:
            relationships = ET.fromstring(package.read(
                "ppt/slides/_rels/" + slide.rsplit("/", 1)[-1] + ".rels"))
            links = [node for node in relationships
                     if node.get("Type", "").endswith("/notesSlide")]
            if len(links) != 1 or links[0].get("TargetMode") == "External":
                raise ValueError("Each synthetic slide needs one local notes relationship")
            target = posixpath.normpath(posixpath.join("ppt/slides", links[0].get("Target", "")))
            if not target.startswith("ppt/notesSlides/") or target in targets:
                raise ValueError("Missing or aliased slide notes part")
            targets.add(target)
            document = ET.fromstring(package.read(target))
            notes.append(" ".join(node.text or "" for node in document.iter()
                                  if node.tag.rsplit("}", 1)[-1] == "t"))
    return notes


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load trusted module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class SourceContracts(unittest.TestCase):
    def text(self, skill):
        return (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")

    def test_content_is_not_a_slide_budget(self):
        text = self.text("generate-write")
        for removed in ("max 40 words per section", "Max 40 words per section",
                        "max 4 bullets", 'First-person plural ("vi")'):
            self.assertNotIn(removed, text)
        for retained in ("**Body:**", "**Bullets:**", "source_outline_hash",
                         "source_content_hash", "{#sec-1}", "<!-- key_message:"):
            self.assertIn(retained, text)
        self.assertIn("multi-paragraph", text)
        self.assertIn("material limitations", text)

    def test_outline_counts_and_language_are_not_universal_limits(self):
        text = self.text("generate-outline")
        self.assertNotIn("--language <sv|en>", text)
        self.assertNotIn("section_count 5-8", text)
        self.assertNotIn("Total within \u00b12 of slide_count_target", text)
        for field in ("slide_count_target", "source_brief_hash", "source_material", "voice_technique"):
            self.assertIn(field, text)

    def test_standalone_native_paths_and_flags_are_documented(self):
        for name in ("generate-word", "generate-ppt"):
            text = self.text(name)
            for flag in ("--brief", "--from-pipeline", "--out", "--use-defaults", "--template",
                         "--audience", "--voice", "--ignore-stale-brand"):
                self.assertIn(flag, text)
            for operation in ("list_canvas_capabilities", "open_canvas", "get_model", "batch"):
                self.assertIn(operation, text)
            self.assertNotIn("npm i -g", text)
            self.assertNotIn("ALL GATES PASS", text)
            self.assertNotIn("capabilities \u2212 2", text)
            self.assertNotIn("~/.lintel/draft/", text)
        native = (ROOT / "skills/generate-ppt/references/native-powerpoint.md").read_text(encoding="utf-8")
        self.assertIn("separate serialized calls", native)
        self.assertIn("aliased", native)

    def test_qa_never_repairs_by_discarding_content(self):
        text = self.text("generate-qa")
        self.assertNotIn("Truncate bullets", text)
        self.assertNotIn("qa_pass: (errors == 0)", text)
        self.assertIn("qa_requirements", text)
        self.assertIn("unverified", text)
        self.assertIn("render", text.lower())
        self.assertIn("source", text.lower())

    def test_orchestrator_distinguishes_available_and_unverified_formats(self):
        text = self.text("generate")
        self.assertNotIn("slot path: operator-AI generates", text)
        self.assertNotIn("Block on any gate failure or vocabulary-blocklist hits", text)
        self.assertIn("A15.3.shared", text)
        self.assertIn("mandatory", text)

    def test_fixture_is_long_and_bound_without_a_new_content_schema(self):
        with tempfile.TemporaryDirectory(dir=RUN, prefix="source-") as name:
            root = Path(name)
            write_fixture(root)
            self.assertGreater(len((root / "brief.md").read_text().split()), 1100)
            self.assertTrue(all(len(p.split()) > 40 for _, ps in SECTIONS for p in ps))
            for child, parent, field in (("outline.md", "brief.md", "source_brief_hash"),
                                         ("content.md", "outline.md", "source_outline_hash"),
                                         ("speaker-notes.md", "content.md", "source_content_hash")):
                self.assertIn(field + ": " + hashlib.sha256((root / parent).read_bytes()).hexdigest(),
                              (root / child).read_text(encoding="utf-8"))
            with self.assertRaises(FileExistsError):
                write_fixture(root)


class ControlContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=RUN, prefix="case-")
        self.base = Path(self.tmp.name)
        self.addCleanup(self.cleanup)
        self.repo, self.home = self.base / "r", self.base / "h"
        self.repo.mkdir()
        self.home.mkdir()
        self.config = PC.ProfileConfig(
            ROOT, self.repo, self.home, self.home / "packs", self.home / "packs/active-pack",
            context_id="p12-synthetic",
        )
        self.pin = PC.bootstrap_profile_context(self.config)
        self.reference = PC.profile_reference(self.pin)
        self.policy = PC.required_policy(self.pin)

    def cleanup(self):
        root = self.base.absolute()
        self.assertEqual(root.parent, RUN.absolute())
        self.assertTrue(root.name.startswith("case-"))
        if os.name == "nt":
            self.tmp.name = "\\\\?\\" + str(root)
        self.tmp.cleanup()

    def control(self, status="pass", requirement="mandatory", applicability="applicable"):
        return {
            "id": "rendered-layout", "kind": "check", "requirement": requirement,
            "applicability": applicability, "status": status,
            "reason": "Synthetic test observation, not a native rendering receipt.",
            "policy": {"source": "P12.md", "version": "3ee602f", "applicability": "Requested rendered inspection",
                       "jurisdiction": None, "actor": None, "effective_date": None},
            "evidence": ["observation.txt"], "observation": {},
        }

    def test_neutral_profile_does_not_invent_voice_or_brand_gates(self):
        self.assertEqual(self.reference["name"], "_default")
        self.assertEqual(self.pin["profile"]["values"]["voice"]["gates_active"], [])
        self.assertFalse(self.policy["required"])
        result = RC.evaluate_controls([], required_policy=self.policy)
        self.assertEqual(result["assurance"], "no_applicable_controls")
        self.assertEqual(result["status"], "unverified")
        self.assertFalse((self.home / "profile.yaml").exists())

    def test_missing_mandatory_rendering_cannot_be_scored_into_pass(self):
        for status in ("unverified", "error", "fail"):
            check = self.control(status)
            check["advisory_score"] = 100
            self.assertTrue(RC.evaluate_controls([check], required_policy=self.policy)["blocked"])

    def test_optional_style_failure_is_not_a_new_mandatory_gate(self):
        check = self.control("fail", "advisory")
        result = RC.evaluate_controls([check], required_policy=self.policy)
        self.assertFalse(result["blocked"])
        self.assertTrue(result["advisories"])

    def test_unknown_or_ungrounded_applicability_blocks(self):
        check = self.control(applicability="unknown")
        self.assertTrue(RC.evaluate_controls([check], required_policy=self.policy)["blocked"])
        check = self.control(applicability="not_applicable")
        check["evidence"] = []
        self.assertTrue(RC.evaluate_controls([check], required_policy=self.policy)["blocked"])

    def test_required_profile_failure_is_not_neutral_fallback(self):
        (self.repo / ".claude").mkdir(exist_ok=True)
        (self.repo / ".claude/profile-requirements.json").write_text(
            '{"schema_version":1,"required_pack":"missing-synthetic"}', encoding="utf-8")
        with self.assertRaises(PC.ProfileError):
            PC.resolve_profile(self.config)
        with self.assertRaises(PC.ProfileError):
            PC.verify_profile_reference(self.reference, self.config)

    def test_changed_source_and_output_revoke_bound_qa(self):
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(self.base))
        git = shutil.which("git")
        self.assertIsNotNone(git)
        def run(*args, cwd=None):
            result = subprocess.run([git, *args], cwd=cwd or self.repo, env=env,
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout.strip()
        outside = subprocess.run([git, "rev-parse", "--show-toplevel"], cwd=self.home, env=env,
                                 capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(outside.returncode, 0, "Fixture discovered an ancestor repository")
        run("init", "--quiet", "--template=" + str(RUN / "empty-hooks"))
        self.assertEqual(Path(run("rev-parse", "--show-toplevel")).resolve(), self.repo.resolve())
        (self.repo / "P12.md").write_bytes(
            (ROOT / ".claude/plans/universal-implementation/packages/P12.md").read_bytes())
        run("add", "P12.md")
        run("-c", "user.name=Synthetic P12", "-c", "user.email=p12@example.invalid",
            "commit", "--quiet", "-m", "test: synthetic document context")
        write_fixture(self.repo)
        (self.repo / "artifact.txt").write_text("Synthetic control data; not an Office artifact.", encoding="utf-8")
        (self.repo / "observation.txt").write_text("Synthetic control test.", encoding="utf-8")
        check = self.control()
        request = {
            "work_map": None, "package_id": "P12", "leaf_ids": ["A15.2"],
            "acceptance_paths": ["P12.md"], "base": run("rev-parse", "HEAD"),
            "selection": ["brief.md", "content.md", "artifact.txt"], "record_path": None,
            "attempt_id": "p12-contract-test", "builder": {"id": "synthetic", "context": "test"},
            "independence_required": True, "purpose": "implementation",
            "profile": self.reference, "required_policy": self.policy,
            "required_controls": ["rendered-layout"],
            "qa_requirements": [{key: check[key] for key in ("id", "kind", "requirement", "applicability", "policy")}],
        }
        old_ceiling = os.environ["GIT_CEILING_DIRECTORIES"]
        os.environ["GIT_CEILING_DIRECTORIES"] = str(self.base)
        try:
            context = CLI.prepare(self.repo, request)
            qa = {"schema_version": 2, "context_digest": RC.content_digest(context), "controls": [check],
                  "evidence": RC.evidence_manifest(self.repo, [check])}
            PC.verify_profile_reference(context["profile"], self.config)
            self.assertFalse(RC.verify_qa(self.repo, qa, expected=context)["blocked"])
            changed = deepcopy(qa)
            changed["controls"][0]["requirement"] = "advisory"
            with self.assertRaises(RC.ContractError):
                RC.verify_qa(self.repo, changed, expected=context)
            for name in ("brief.md", "content.md", "artifact.txt"):
                path = self.repo / name
                original = path.read_bytes()
                path.write_bytes(original + b"\nchanged")
                with self.assertRaises(RC.ContractError):
                    RC.verify_qa(self.repo, qa, expected=context)
                path.write_bytes(original)
        finally:
            os.environ["GIT_CEILING_DIRECTORIES"] = old_ceiling


class NativeRetention(unittest.TestCase):
    """Run only on explicitly supplied, previously created synthetic native artifacts."""
    def test_full_body_tables_claims_citations_and_limitation(self):
        for extension in ("docx", "pptx"):
            parts = document_text(OPTIONS.native_artifacts / ("long-technical-brief." + extension))
            self.assertEqual(missing_content(parts), [], extension)

    def test_long_source_is_in_actual_slide_notes(self):
        parts = document_text(OPTIONS.native_artifacts / "long-technical-brief.pptx")
        notes = {name: text for name, text in parts.items() if "/notesSlides/" in name}
        self.assertGreaterEqual(len(notes), len(SECTIONS))
        self.assertEqual(missing_content(notes), [])
        ordered = slide_notes(OPTIONS.native_artifacts / "long-technical-brief.pptx")
        for index, (_, paragraphs) in enumerate(SECTIONS):
            for paragraph in paragraphs:
                self.assertIn(paragraph, ordered[index])

    def test_editable_table_cells_are_not_just_text_mentions(self):
        word_ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        drawing_ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
        with ZipFile(OPTIONS.native_artifacts / "long-technical-brief.docx") as package:
            document = ET.fromstring(package.read("word/document.xml"))
            tables = document.findall(".//w:tbl", word_ns)
            actual = [tuple(tuple("".join(cell.itertext()) for cell in row.findall("w:tc", word_ns))
                            for row in table.findall("w:tr", word_ns)) for table in tables]
            self.assertEqual(actual, [CAPACITY, CLAIMS])
        with ZipFile(OPTIONS.native_artifacts / "long-technical-brief.pptx") as package:
            document = ET.fromstring(package.read("ppt/slides/slide3.xml"))
            tables = document.findall(".//a:tbl", drawing_ns)
            actual = [tuple(tuple("".join(cell.itertext()) for cell in row.findall("a:tc", drawing_ns))
                            for row in table.findall("a:tr", drawing_ns)) for table in tables]
            self.assertEqual(actual, [CAPACITY])

    def test_each_lost_reasoning_citation_cell_or_limitation_is_detected(self):
        for extension in ("docx", "pptx"):
            parts = document_text(OPTIONS.native_artifacts / ("long-technical-brief." + extension))
            for lost in (SECTIONS[1][1][1], SECTIONS[3][1][0], REFERENCES[1], CLAIMS[3][2]):
                damaged = {name: text.replace(lost, "") for name, text in parts.items()}
                self.assertIn(lost, missing_content(damaged))

    def test_slides_without_notes_do_not_pass_on_short_visible_copy(self):
        parts = document_text(OPTIONS.native_artifacts / "long-technical-brief.pptx")
        visible = {name: text for name, text in parts.items() if "/slides/" in name}
        self.assertTrue(missing_content(visible))

    def test_native_notes_part_alias_is_rejected(self):
        source = OPTIONS.native_artifacts / "long-technical-brief.pptx"
        with tempfile.TemporaryDirectory(dir=RUN, prefix="negative-") as name:
            destination = Path(name) / "aliased.pptx"
            with ZipFile(source) as original, ZipFile(destination, "w", ZIP_DEFLATED) as altered:
                for entry in original.infolist():
                    data = original.read(entry.filename)
                    if entry.filename == "ppt/slides/_rels/slide2.xml.rels":
                        xml = ET.fromstring(data)
                        for relationship in xml:
                            if relationship.get("Type", "").endswith("/notesSlide"):
                                relationship.set("Target", "../notesSlides/notesSlide1.xml")
                        data = ET.tostring(xml, encoding="utf-8", xml_declaration=True)
                    altered.writestr(entry, data)
            with self.assertRaisesRegex(ValueError, "aliased"):
                slide_notes(destination)


def main() -> int:
    global OPTIONS, RUN, RC, PC, CLI
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-root", type=Path, default=Path(tempfile.gettempdir()),
                        help="Parent for a new isolated test root; defaults to the system temporary directory.")
    parser.add_argument("--write-fixture", type=Path)
    parser.add_argument("--native-artifacts", type=Path)
    OPTIONS = parser.parse_args()
    parent = OPTIONS.fixture_root.resolve()
    parent.mkdir(parents=True, exist_ok=True)
    RUN = Path(tempfile.mkdtemp(prefix="p12-", dir=parent))
    roots = {name: RUN / name for name in ("home", "app", "localapp", "temp", "lintel", "target", "empty-hooks")}
    for path in roots.values():
        path.mkdir()
    git = shutil.which("git")
    if not git:
        raise RuntimeError("Git is required for document evidence contract tests")
    path = os.pathsep.join(dict.fromkeys((str(Path(git).parent), str(Path(sys.executable).parent), os.defpath)))
    environment = {
        "PATH": path, "HOME": str(roots["home"]), "USERPROFILE": str(roots["home"]),
        "APPDATA": str(roots["app"]), "LOCALAPPDATA": str(roots["localapp"]),
        "TEMP": str(roots["temp"]), "TMP": str(roots["temp"]), "TMPDIR": str(roots["temp"]),
        "LINTEL_HOME": str(roots["lintel"]), "LINTEL_SOURCE_ROOT": str(ROOT),
        "LINTEL_REPO_ROOT": str(roots["target"]), "LINTEL_PROFILE_CONTEXT": "p12-synthetic",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(RUN / "empty.gitconfig"),
        "GIT_CEILING_DIRECTORIES": str(RUN), "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_COUNT": "4", "GIT_CONFIG_KEY_0": "core.hooksPath",
        "GIT_CONFIG_VALUE_0": str(roots["empty-hooks"]), "GIT_CONFIG_KEY_1": "core.autocrlf",
        "GIT_CONFIG_VALUE_1": "false", "GIT_CONFIG_KEY_2": "commit.gpgSign",
        "GIT_CONFIG_VALUE_2": "false", "GIT_CONFIG_KEY_3": "core.fsmonitor",
        "GIT_CONFIG_VALUE_3": "false", "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
    }
    if os.name == "nt":
        environment.update(SystemRoot="C:\\Windows", WINDIR="C:\\Windows",
                           ComSpec="C:\\Windows\\System32\\cmd.exe",
                           HOMEDRIVE=roots["home"].drive, HOMEPATH=str(roots["home"])[2:])
    os.environ.clear()
    os.environ.update(environment)
    tempfile.tempdir = str(roots["temp"])
    (RUN / "empty.gitconfig").write_text("", encoding="utf-8")
    closure = {}
    document_sources = tuple(f"skills/{name}/SKILL.md" for name in (
        "generate-outline", "generate-write", "generate-word", "generate-ppt", "generate", "generate-qa",
    )) + (
        "skills/generate-write/references/fidelity-and-evidence.md",
        "skills/generate-word/references/native-word.md",
        "skills/generate-ppt/references/native-powerpoint.md",
        "tests/integration/document-format-pipeline.py",
        "tests/integration/document-format-pipeline.sh",
    )
    for relative in SOURCE_CLOSURE + document_sources:
        source = ROOT / relative
        if not source.is_file() or source.is_symlink():
            raise RuntimeError(f"Trusted dependency missing or linked: {source}")
        closure[relative] = hashlib.sha256(source.read_bytes()).hexdigest()
    (RUN / "preflight.json").write_text(json.dumps({
        "environment": environment, "source": str(ROOT), "source_sha256": closure,
        "native_artifacts": str(OPTIONS.native_artifacts) if OPTIONS.native_artifacts else None,
        "layer": "Instruction/control tests and optional OOXML retention; NOT native render/reopen evidence.",
    }, indent=2), encoding="utf-8")
    print(f"preflight: {RUN / 'preflight.json'}", flush=True)
    if OPTIONS.write_fixture:
        write_fixture(OPTIONS.write_fixture.resolve())
        print(f"synthetic source: {OPTIONS.write_fixture.resolve()}")
        return 0
    sys.path.insert(0, str(ROOT / "lib"))
    RC = load_module("review_contract", ROOT / "lib/review_contract.py")
    PC = load_module("p12_profile_context", ROOT / "lib/profile_context.py")
    CLI = load_module("p12_review_cli", ROOT / "bin/li-review-evidence.py")
    suite = unittest.TestSuite()
    for case in (SourceContracts, ControlContracts):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(case))
    if OPTIONS.native_artifacts:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(NativeRetention))
    else:
        print("Native artifacts not supplied: render, reopen/edit and native retention acceptance remain open.")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    (RUN / "result.json").write_text(json.dumps({
        "executed": result.testsRun, "failed": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "success": result.wasSuccessful(),
        "native_actions_executed_by_tests": False,
        "remaining_case_directories": sorted(path.name for path in RUN.glob("case-*")),
    }, indent=2), encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
