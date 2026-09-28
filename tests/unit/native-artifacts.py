#!/usr/bin/env python3
# component: native-artifact-tests
# implements: ADR-0039
# intent: .claude/plans/native-client-parity/spec.md
# constraints: synthetic source trees only; stdlib unittest; no network, host session or model call
# last_intent_review: 2026-09-28
"""Native Copilot rendering: host profile, frontmatter, preamble, transforms and link policy."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("li_copilot_native", ROOT / "bin/li-copilot.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
HOST = adapter.NATIVE_HOSTS["copilot"]
REPOSITORY = "https://github.com/jokerman89/lintel"
# Independent oracle: the exact text of spec.md "Skill preamble", with the skill-relative paths bullet.
SPEC_SKILL_PREAMBLE = """> **Lintel on GitHub Copilot.** Generated from `{canonical}`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `{root}` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** `<base>` and this skill's `scripts/`, `references/` and `data/` mean
>   `{root}/skills/{name}/` in the Lintel source, not this generated folder.
>   `${{LINTEL_SKILLS_DIR:-skills}}` means the skills root, `{root}/skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/{name}/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.
"""
# The spec's agent preamble: the same Resource root and Shell steps bullets (the root is relative
# to the agent file's folder, so the skill-directory phrase names it), plus the delegation line.
SPEC_AGENT_PREAMBLE = """> - **Resource root:** `{root}` from this agent's directory, `.github/agents/` (the Lintel source
>   with `bin/`, `lib/`, `skills/`). Write plans, state and evidence into the working repository's
>   `.claude/` tree, never into the resource root.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
>
> You were delegated by a Lintel workflow; stay inside the supplied task and report changed files,
> checks run, findings by severity and limitations.
"""
CANONICAL_HEADER = """---
name: {name}
layer: foundation
description: {description}
color: cyan
tools: Read, Write, Edit, Bash
voice: internal
cli_support: [claude-code, codex, copilot]
necessity: REQUIRED
gap_if_skipped: "Nothing is planned."
---
"""
AGENT_HEADER = """---
name: {name}
category: engineering
description: {description}
color: blue
tools: Read, Grep, Glob, Bash
voice: internal
cli_support: [claude-code]
tier: sonnet
memory: project
---
"""


def frontmatter_keys(data: bytes) -> list[str]:
    lines, _ = adapter.split_frontmatter(data.decode("utf-8"))
    return [line.split(":", 1)[0] for line in lines]


def skill_preamble(root: str, name: str = "plan") -> str:
    return SPEC_SKILL_PREAMBLE.format(canonical=f"skills/{name}/SKILL.md", root=root, name=name)


class NativeArtifacts(unittest.TestCase):
    def setUp(self):
        sandbox = tempfile.TemporaryDirectory(prefix="lintel-native-")
        self.addCleanup(sandbox.cleanup)
        self.source = Path(sandbox.name).resolve() / "source"
        for name in adapter.WORKFLOWS:
            self.skill(name, f"Canonical {name} description.", f"\n# {name}\n\nThe canonical {name} method.\n")
        self.write("skills/define/references/intake.md", "# Intake\n")
        self.write(".claude/decisions/x.md", "# Decision\n\n## a\n")
        self.write(".claude-plugin/plugin.json", json.dumps({"repository": REPOSITORY}))

    def write(self, relative: str, text: str) -> None:
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))

    def skill(self, name: str, description: str, body: str) -> None:
        self.write(f"skills/{name}/SKILL.md", CANONICAL_HEADER.format(name=name, description=description) + body)

    def agent(self, category: str, name: str, body: str, description: str = "Reviews a change.") -> None:
        self.write(f"agents/{category}/{name}.md", AGENT_HEADER.format(name=name, description=description) + body)

    def render(self, name: str, *, local: bool = True, files=None) -> str:
        generated, data = adapter.native_skill_file(self.source, name, files or {}, local,
                                               None if local else REPOSITORY, HOST)
        self.assertEqual(generated, f".github/skills/li-{name}/SKILL.md")
        self.assertTrue(data.endswith(b"\n") and not data.endswith(b"\n\n") and b"\r" not in data)
        return data.decode("utf-8")

    def body(self, rendered: str, preamble: str) -> str:
        _, body = adapter.split_frontmatter(rendered)
        self.assertTrue(body.startswith("\n" + preamble), body[:400])
        return body[len("\n" + preamble):]

    def test_copilot_host_profile_equals_the_spec(self):  # 1.1.a
        self.assertEqual(adapter.NATIVE_HOSTS["copilot"], {
            "skill_root": ".github/skills", "skill_name": "li-{name}",
            "agent_root": ".github/agents", "agent_file": "{name}.agent.md",
            "invocation": "/li-{name}",
            "tool_rewrites": {"AskUserQuestion": "ask_user"},
            "skill_frontmatter": ("name", "description"),
            "agent_frontmatter": ("name", "description", "tools"),
            "agent_body_limit": 30000, "description_limit": 1024,
        })

    def test_split_frontmatter_returns_lines_and_untouched_body(self):  # 1.1.b
        lines, body = adapter.split_frontmatter("---\nname: plan\ndescription: x\n---\n\n# Plan\n---\ntail\n")
        self.assertEqual(lines, ["name: plan", "description: x"])
        self.assertEqual(body, "\n# Plan\n---\ntail\n")
        self.assertEqual(adapter.split_frontmatter("---\nname: x\n---")[1], "")

    def test_split_frontmatter_rejects_missing_and_unterminated_headers(self):  # 1.1.b
        for text in ("# No frontmatter\n\nname: plan\n", "", "\n---\nname: plan\n---\n", " ---\nname: x\n---\n"):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, "Missing frontmatter"):
                adapter.split_frontmatter(text)
        with self.assertRaisesRegex(ValueError, "Unterminated frontmatter"):
            adapter.split_frontmatter("---\nname: plan\ndescription: never closed\n")

    def test_skill_frontmatter_has_exactly_name_and_description(self):  # 1.1.c
        self.skill("verify", "Use to verify changes without editing them.", "\n# Verify\n")
        core, other = self.render("plan"), self.render("verify")
        for rendered in (core, other):
            self.assertEqual(frontmatter_keys(rendered.encode("utf-8")), ["name", "description"])
        self.assertTrue(core.startswith(f"---\nname: li-plan\ndescription: {adapter.WORKFLOWS['plan']}\n---\n\n"))
        self.assertTrue(other.startswith(
            "---\nname: li-verify\ndescription: Use to verify changes without editing them.\n---\n\n"))
        for dropped in ("layer:", "color:", "tools:", "voice:", "cli_support:", "necessity:", "gap_if_skipped:"):
            self.assertNotIn(dropped, core.split("\n---\n", 1)[0])

    def test_skill_description_limit_and_quoted_canonical_description(self):  # 1.1.c
        self.skill("limit", "d" * 1024, "\n# At the limit\n")
        self.assertIn("\ndescription: " + "d" * 1024 + "\n", self.render("limit"))
        self.skill("limit", "d" * 1025, "\n# Over the limit\n")
        with self.assertRaisesRegex(ValueError, "exceeds 1024 characters: skills/limit/SKILL.md"):
            self.render("limit")
        self.skill("quoted", '"Quoted: a colon-space value."', "\n# Quoted\n")
        self.assertIn('\ndescription: "Quoted: a colon-space value."\n', self.render("quoted"))
        self.write("skills/mismatch/SKILL.md", CANONICAL_HEADER.format(name="other", description="x") + "\n")
        with self.assertRaisesRegex(ValueError, "must match its folder"):
            self.render("mismatch")

    def test_descriptions_use_the_host_invocation_and_tool_spelling(self):  # 1.1.c, 1.3.b
        self.skill("verify", "Use after /li:build; confirm with AskUserQuestion.", "\n# Verify\n")
        self.assertIn("\ndescription: Use after /li-build; confirm with ask_user.\n", self.render("verify"))
        self.agent("doc-gen", "PPTNarrativeArchitect", "\nDesigns the arc.\n",
                   description="Use before /li:generate-ppt runs.")
        _, _, data = adapter.native_agent_file(self.source, "agents/doc-gen/PPTNarrativeArchitect.md", {}, True,
                                               None, HOST)
        self.assertIn(b"\ndescription: Use before /li-generate-ppt runs.\n", data)
        self.assertNotIn(b"/li:", data)

    def test_skill_preamble_has_the_exact_root_in_both_modes(self):  # 1.1.d, skill-relative paths
        bundled = {".github/lintel/skills/define/references/intake.md": b"# Intake\n"}
        for local, root, files in ((True, "../../..", {}), (False, "../../lintel", bundled)):
            with self.subTest(local=local):
                preamble = skill_preamble(root)
                self.assertEqual(adapter.SKILL_PREAMBLE.format(canonical="skills/plan/SKILL.md", root=root,
                                                               name="plan"), preamble)
                rendered = self.render("plan", local=local, files=files)
                self.assertEqual(self.body(rendered, preamble), "\n# plan\n\nThe canonical plan method.\n")
                # The skill-relative bullet follows Resource root: this skill's own folder, the skills
                # root that ${LINTEL_SKILLS_DIR:-skills} names, and the pinned variable for li-run steps.
                self.assertIn("never into the resource root.\n> - **Skill-relative paths:** `<base>` and "
                              "this skill's `scripts/`, `references/` and `data/` mean\n"
                              f">   `{root}/skills/plan/` in the Lintel source, not this generated folder.\n"
                              f">   `${{LINTEL_SKILLS_DIR:-skills}}` means the skills root, `{root}/skills`. "
                              "A `bin/li-run` step\n>   runs in the working repository, so use "
                              "`$LINTEL_SKILLS_DIR/plan/` there.\n> - **Shell steps:**", rendered)
                define = self.render("define", local=local, files=files)
                self.assertEqual(self.body(define, skill_preamble(root, "define")),
                                 "\n# define\n\nThe canonical define method.\n")
                self.assertIn(f"\n>   `{root}/skills/define/` in the Lintel source", define)
                self.assertIn("so use `$LINTEL_SKILLS_DIR/define/` there.\n", define)

    def test_skill_relative_bullet_fits_100_columns_for_the_longest_skill_name(self):  # N1
        # The longest name comes from canonical discovery, so a longer future skill is measured too.
        names = sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md"))
        self.assertTrue(names, "no canonical skills discovered")
        longest = max(names, key=len)
        self.skill(longest, "The longest canonical skill name.", "\n# Longest\n")
        bundled = {".github/lintel/skills/define/references/intake.md": b"# Intake\n"}
        for local, root, files in ((True, "../../..", {}), (False, "../../lintel", bundled)):
            with self.subTest(local=local, name=longest):
                rendered = self.render(longest, local=local, files=files)
                start = rendered.index("> - **Skill-relative paths:**")
                bullet = rendered[start:rendered.index("> - **Shell steps:**", start)].splitlines()
                self.assertEqual([(len(line), line) for line in bullet if len(line) > 100], [])
                self.assertEqual(len(bullet), 4)
                self.assertIn(f"`{root}/skills/{longest}/`", bullet[1])
                self.assertIn(f"`$LINTEL_SKILLS_DIR/{longest}/`", bullet[3])
                self.body(rendered, skill_preamble(root, longest))

    def test_invocation_and_tool_transforms_change_nothing_else(self):  # 1.1.e
        original = ("Run /li:plan, then /li:<phase> or `/li:build --resume`.\r\n"
                    "Ask with AskUserQuestion; keep li:plan, /li: and /lint:plan — é ✓\n")
        expected = ("Run /li-plan, then /li-<phase> or `/li-build --resume`.\r\n"
                    "Ask with ask_user; keep li:plan, /li: and /lint:plan — é ✓\n")
        self.assertEqual(adapter.native_text(original, HOST), expected)
        body = "\n# Plan\n\nUse /li:plan and /li:<phase>.\nAskUserQuestion: confirm?\n\n```bash\nlintel /li:review\n```\n"
        self.skill("plan", "Plans.", body)
        preamble = skill_preamble("../../..")
        self.assertEqual(self.body(self.render("plan"), preamble), body.replace("/li:plan", "/li-plan")
                         .replace("/li:<phase>", "/li-<phase>").replace("AskUserQuestion", "ask_user")
                         .replace("/li:review", "/li-review"))

    def test_local_links_are_rebased_from_the_generated_directory(self):  # 1.2.a
        self.skill("plan", "Plans.", "\n[Intake](../define/references/intake.md#start)\n"
                   "[Decision][x]\n[Section](#local) [Site](https://example.invalid/a.md)\n"
                   "`[Code](../define/references/intake.md)`\n\n[x]: ../../.claude/decisions/x.md\n")
        body = self.body(self.render("plan"), skill_preamble("../../.."))
        self.assertEqual(body, "\n[Intake](../../../skills/define/references/intake.md#start)\n"
                         "[Decision][x]\n[Section](#local) [Site](https://example.invalid/a.md)\n"
                         "`[Code](../define/references/intake.md)`\n\n[x]: ../../../.claude/decisions/x.md\n")
        resolved = (self.source / ".github/skills/li-plan" / "../../../skills/define/references/intake.md").resolve()
        self.assertEqual(resolved, (self.source / "skills/define/references/intake.md").resolve())
        self.skill("plan", "Plans.", "\n[Missing](../define/references/absent.md)\n")
        with self.assertRaisesRegex(ValueError, "Missing canonical link target: skills/plan/SKILL.md"):
            self.render("plan")

    def test_directory_links_render_and_verify_only_when_the_directory_exists(self):  # L1
        self.skill("plan", "Plans.", "\n[References](../define/references/)\n")
        rendered = self.render("plan")
        self.assertIn("\n[References](../../../skills/define/references/)\n", rendered)
        generated = {".github/skills/li-plan/SKILL.md": rendered.encode("utf-8")}
        self.assertEqual(adapter.verify_links(generated, self.source), [])
        absent = {".github/skills/li-plan/SKILL.md": b"[Absent](../../../skills/define/absent/)\n"}
        self.assertEqual(adapter.verify_links(absent, self.source),
                         ["Missing generated link: .github/skills/li-plan/SKILL.md -> ../../../skills/define/absent/"])
        self.skill("plan", "Plans.", "\n[Absent](../define/absent/)\n")
        with self.assertRaisesRegex(ValueError, "Missing canonical link target: skills/plan/SKILL.md"):
            self.render("plan")

    def test_vendored_links_stay_bundled_or_become_public_urls(self):  # 1.2.b
        self.skill("plan", "Plans.", "\n[Intake](../define/references/intake.md)\n"
                   "[Decision](../../.claude/decisions/x.md#a)\n[Tests](../../tests/)\n"
                   "[Skills](../)\n")
        files = {".github/lintel/skills/define/references/intake.md": b"# Intake\n",
                 ".github/lintel/skills/plan/SKILL.md": b"canonical copy\n"}
        body = self.body(self.render("plan", local=False, files=files), skill_preamble("../../lintel"))
        self.assertEqual(body, "\n[Intake](../../lintel/skills/define/references/intake.md)\n"
                         f"[Decision]({REPOSITORY}/blob/main/.claude/decisions/x.md#a)\n"
                         f"[Tests]({REPOSITORY}/tree/main/tests)\n[Skills](../../lintel/skills/)\n")
        self.skill("plan", "Plans.", "\n[Unbundled method](../define/references/absent.md)\n")
        with self.assertRaisesRegex(ValueError, "Missing bundled source target: skills/plan/SKILL.md"):
            self.render("plan", local=False, files=files)

    def test_query_strings_survive_rebasing_in_both_modes(self):  # L2
        self.skill("plan", "Plans.", "\n[Intake](../define/references/intake.md?plain=1#L3)\n"
                   "[Decision](../../.claude/decisions/x.md?plain=1#a)\n")
        self.assertEqual(self.body(self.render("plan"), skill_preamble("../../..")),
                         "\n[Intake](../../../skills/define/references/intake.md?plain=1#L3)\n"
                         "[Decision](../../../.claude/decisions/x.md?plain=1#a)\n")
        files = {".github/lintel/skills/define/references/intake.md": b"# Intake\n"}
        self.assertEqual(self.body(self.render("plan", local=False, files=files), skill_preamble("../../lintel")),
                         "\n[Intake](../../lintel/skills/define/references/intake.md?plain=1#L3)\n"
                         f"[Decision]({REPOSITORY}/blob/main/.claude/decisions/x.md?plain=1#a)\n")

    def test_agents_keep_the_allowlist_preamble_and_transformed_body(self):  # 1.3.b
        self.agent("engineering", "CodeReviewer", "\nYou review.\nAsk with AskUserQuestion; run /li:review.\n"
                   "See [evidence](../../skills/define/references/intake.md).\n")
        bundled = {".github/lintel/skills/define/references/intake.md": b"# Intake\n"}
        for local, root, link, files in ((True, "../..", "../../skills/define/references/intake.md", {}),
                                         (False, "../lintel", "../lintel/skills/define/references/intake.md", bundled)):
            with self.subTest(local=local):
                name, generated, data = adapter.native_agent_file(self.source, "agents/engineering/CodeReviewer.md",
                                                             files, local, None if local else REPOSITORY, HOST)
                self.assertEqual((name, generated), ("CodeReviewer", ".github/agents/CodeReviewer.agent.md"))
                self.assertEqual(frontmatter_keys(data), ["name", "description", "tools"])
                text = data.decode("utf-8")
                self.assertTrue(text.startswith("---\nname: CodeReviewer\ndescription: Reviews a change.\n"
                                                "tools: Read, Grep, Glob, Bash\n---\n\n"))
                preamble = SPEC_AGENT_PREAMBLE.format(root=root)
                self.assertEqual(adapter.AGENT_PREAMBLE.format(canonical="agents/engineering/CodeReviewer.md",
                                                               root=root), preamble)
                shell_steps = SPEC_SKILL_PREAMBLE[SPEC_SKILL_PREAMBLE.index("> - **Shell steps:**"):
                                                  SPEC_SKILL_PREAMBLE.index("> - **Tools:**")]
                self.assertIn(shell_steps, preamble)
                _, body = adapter.split_frontmatter(text)
                self.assertNotIn("Skill-relative paths", text)  # an agent has no skill folder
                self.assertEqual(body, "\n" + preamble + "\nYou review.\nAsk with ask_user; run /li-review.\n"
                                 f"See [evidence]({link}).\n")

    def test_agent_body_limit_names_and_collisions_are_errors(self):  # 1.3.b
        preamble = len(adapter.AGENT_PREAMBLE.format(canonical="agents/engineering/Big.md", root="../.."))
        # The generated body is "\n" + preamble + "\n" + filler + "\n" after the frontmatter.
        filler = HOST["agent_body_limit"] - preamble - 3
        self.agent("engineering", "Big", "\n" + "x" * filler)
        _, _, data = adapter.native_agent_file(self.source, "agents/engineering/Big.md", {}, True, None, HOST)
        self.assertEqual(len(adapter.split_frontmatter(data.decode("utf-8"))[1]), HOST["agent_body_limit"])
        self.agent("engineering", "Big", "\n" + "x" * (filler + 1))
        with self.assertRaisesRegex(ValueError, "Agent body exceeds 30000 characters: agents/engineering/Big.md"):
            adapter.native_agent_file(self.source, "agents/engineering/Big.md", {}, True, None, HOST)
        (self.source / "agents/engineering/Big.md").unlink()
        self.write("agents/engineering/Renamed.md", AGENT_HEADER.format(name="Other", description="x") + "\n")
        with self.assertRaisesRegex(ValueError, "must match its file name"):
            adapter.native_agent_file(self.source, "agents/engineering/Renamed.md", {}, True, None, HOST)
        (self.source / "agents/engineering/Renamed.md").unlink()
        self.agent("engineering", "Explorer", "\nFirst.\n")
        self.agent("security", "Explorer", "\nSecond.\n")
        with self.assertRaisesRegex(ValueError, "Native agent name collision"):
            adapter.native_files(self.source, {}, True, HOST)
        (self.source / "agents/security/Explorer.md").unlink()
        self.agent("security", "lintel-planner", "\nShadows a role.\n")
        with self.assertRaisesRegex(ValueError, "Native agent name collision"):
            adapter.native_files(self.source, {}, True, HOST)

    def test_agent_description_limit_is_an_error(self):  # L5
        self.agent("engineering", "Long", "\nReviews.\n", description="d" * 1024)
        _, _, data = adapter.native_agent_file(self.source, "agents/engineering/Long.md", {}, True, None, HOST)
        self.assertIn(b"\ndescription: " + b"d" * 1024 + b"\n", data)
        self.agent("engineering", "Long", "\nReviews.\n", description="d" * 1025)
        with self.assertRaisesRegex(ValueError, "Agent description exceeds 1024 characters: agents/engineering/Long.md"):
            adapter.native_agent_file(self.source, "agents/engineering/Long.md", {}, True, None, HOST)
        with self.assertRaisesRegex(ValueError, "Agent description exceeds 1024 characters"):
            adapter.native_files(self.source, {}, True, HOST)

    def test_every_canonical_skill_and_agent_is_rendered_with_role_agents(self):  # 1.3.a, 1.3.b, 1.3.c
        self.skill("verify", "Verifies.", "\n# Verify\n")
        self.agent("engineering", "CodeReviewer", "\nReviews.\n")
        self.agent("security", "SecurityAuditor", "\nAudits.\n")
        self.write("agents/engineering/README.md", "# Not an agent\n")
        self.write("agents/engineering/_template.md", "---\nname: template\n---\n")
        output = adapter.native_files(self.source, {}, True, HOST)
        skills = sorted(path for path in output if path.startswith(".github/skills/"))
        self.assertEqual(skills, sorted(f".github/skills/li-{name}/SKILL.md"
                                        for name in (*adapter.WORKFLOWS, "verify")))
        agents = sorted(path for path in output if path.startswith(".github/agents/"))
        self.assertEqual(agents, [".github/agents/CodeReviewer.agent.md", ".github/agents/SecurityAuditor.agent.md",
                                  ".github/agents/lintel-builder.agent.md", ".github/agents/lintel-planner.agent.md",
                                  ".github/agents/lintel-reviewer.agent.md"])
        self.assertEqual(list(output), sorted(output))
        for role, workflow in (("planner", "plan"), ("builder", "build"), ("reviewer", "review")):
            text = output[f".github/agents/lintel-{role}.agent.md"].decode("utf-8")
            self.assertEqual(frontmatter_keys(text.encode("utf-8")), ["name", "description"])
            self.assertIn(f"Use the native `/li-{workflow}` skill", text)
            for pointer in ("Copilot adapter contract", "SKILL.md", "](", "/li:"):
                self.assertNotIn(pointer, text)
        (self.source / "skills/resume/SKILL.md").unlink()
        with self.assertRaisesRegex(ValueError, "Required source file is missing"):
            adapter.native_files(self.source, {}, True, HOST)


if __name__ == "__main__":
    unittest.main(verbosity=2)
