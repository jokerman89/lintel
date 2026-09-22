# component: design-browser-pipeline
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P11.md
# constraints: stdlib fixture server, synthetic homes, shared work/profile/control readers
# last_intent_review: 2026-09-22
"""Browser-only A16 verification; static tests never count as live browser observations."""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.request import ProxyHandler, build_opener
from urllib.error import HTTPError
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET


PARSER = argparse.ArgumentParser(description=__doc__)
PARSER.add_argument("--root", type=Path, required=True)
PARSER.add_argument("--out", type=Path)
PARSER.add_argument("--live", action="store_true")
PARSER.add_argument("--browser", type=Path)
OPTIONS = PARSER.parse_args()
ROOT = OPTIONS.root.resolve()
RUNTIME = ROOT / ".claude/runtime"
OUT = (OPTIONS.out or RUNTIME / "p11-a16").resolve()
if not OUT.is_relative_to(RUNTIME.resolve()):
    raise SystemExit("Browser test output must stay in the explicitly owned repository runtime")
OUT.mkdir(parents=True, exist_ok=True)
RUN = Path(tempfile.mkdtemp(prefix="a16-", dir=OUT))
HOME = RUN / "home"
TEMP = RUN / "tmp"
LINTEL = HOME / "lintel"
for directory in (HOME, TEMP, LINTEL / "packs", LINTEL / "audit",
                  HOME / "appdata", HOME / "local", HOME / "config", HOME / "cache"):
    directory.mkdir(parents=True, exist_ok=True)
    if not directory.is_dir() or directory.is_symlink() or not directory.resolve().is_relative_to(RUN):
        raise SystemExit("Synthetic application directory failed ownership preflight")
SESSION_ID = os.environ.get("LINTEL_SESSION_ID", "synthetic-a16-explicit-work")
environment = {key: value for key, value in os.environ.items()
               if key.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT",
                                  "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS", "OS"}}
environment.update({
    "HOME": str(HOME), "USERPROFILE": str(HOME), "HOMEDRIVE": HOME.drive,
    "HOMEPATH": str(HOME)[len(HOME.drive):], "APPDATA": str(HOME / "appdata"),
    "LOCALAPPDATA": str(HOME / "local"), "XDG_CONFIG_HOME": str(HOME / "config"),
    "XDG_CACHE_HOME": str(HOME / "cache"), "TMP": str(TEMP), "TEMP": str(TEMP),
    "TMPDIR": str(TEMP), "LINTEL_SOURCE_ROOT": str(ROOT), "LINTEL_REPO_ROOT": str(ROOT),
    "LINTEL_HOME": str(LINTEL), "LINTEL_PACKS_DIR": str(LINTEL / "packs"),
    "LINTEL_ACTIVE_PACK_FILE": str(LINTEL / "packs/active-pack"),
    "LINTEL_AUDIT_DIR": str(LINTEL / "audit"), "LINTEL_SESSION_ID": SESSION_ID,
    "LINTEL_PROFILE_CONTEXT": SESSION_ID, "LINTEL_PYTHON": sys.executable,
    "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1", "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8", "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": str(HOME / "absent.gitconfig"), "GIT_TERMINAL_PROMPT": "0",
    "GIT_CEILING_DIRECTORIES": os.pathsep.join((str(ROOT), str(RUN))),
})
os.environ.clear()
os.environ.update(environment)
tempfile.tempdir = str(TEMP)
sys.dont_write_bytecode = True

SOURCES = [
    "lib/url_policy.py", "lib/profile_context.py", "lib/native_paths.py",
    "lib/client_capabilities.py", "lib/cli-tiers.yaml", "lib/review_contract.py",
    "lib/review-schema.json", "lib/markdown_source.py", "bin/li-work-artifacts.py",
    "lib/swarm_contract.py", "lib/swarm_snapshot.py", "packs/_default/pack.yaml",
    "skills/browse/scripts/chromium.mjs", "skills/scrape/scripts/extract.mjs",
    "tests/integration/browser-live.mjs", "tests/integration/browser-operations.test.mjs",
    "tests/integration/design-browser-pipeline.py", "tests/integration/design-browser-pipeline.sh",
]


def seal() -> dict[str, str]:
    result = {}
    for relative in SOURCES:
        path = ROOT / relative
        if path.is_symlink() or getattr(path.lstat(), "st_file_attributes", 0) & 0x400:
            raise RuntimeError(f"Linked source refused: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


SEALS = seal()
(RUN / "source-seals.json").write_text(json.dumps(SEALS, indent=2), encoding="utf-8")
(RUN / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
sys.path.insert(0, str(ROOT / "lib"))
from client_capabilities import load_registry, resolve  # noqa: E402
from profile_context import (  # noqa: E402
    ProfileConfig, ProfileError, bootstrap_profile_context, profile_reference,
    required_policy, verify_profile_reference,
)
from review_contract import bind_work, evaluate_controls  # noqa: E402

WORK_MAP = ".claude/plans/universal-implementation/work.json"
SPEC = importlib.util.spec_from_file_location("a16_work_map", ROOT / "bin/li-work-artifacts.py")
WORK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WORK)
CONFIG = ProfileConfig(ROOT, ROOT, LINTEL, LINTEL / "packs",
                       LINTEL / "packs/active-pack", context_id=SESSION_ID)
PROFILE = bootstrap_profile_context(CONFIG)
REFERENCE = profile_reference(PROFILE)
POLICY = required_policy(PROFILE)
WORK.load_work_map(ROOT, Path(WORK_MAP))
WORK_IDENTITY = bind_work(ROOT, work_map=WORK_MAP, package_id="P11",
                         leaf_ids=["A16.1", "A16.2", "A16.3", "A16.4"],
                         acceptance_paths=[".claude/plans/universal-implementation/packages/P11.md"])


def command(argv: list[str], name: str, *, check: bool = True) -> subprocess.CompletedProcess:
    log = RUN / f"{name}.log"
    with log.open("x", encoding="utf-8") as output:
        result = subprocess.run(argv, cwd=ROOT, env=environment, stdout=output,
                                stderr=subprocess.STDOUT, text=True, timeout=300)
    (RUN / f"{name}-command.json").write_text(
        json.dumps({"argv": argv, "exit_code": result.returncode}, indent=2), encoding="utf-8")
    if check and result.returncode:
        raise AssertionError(f"{name} exited {result.returncode}; full output: {log}")
    return result


revision = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          env=environment, text=True, capture_output=True, check=True).stdout.strip()
CONTEXT = {"session_id": SESSION_ID, "work_map": WORK_MAP, "profile_ref": REFERENCE,
           "source_revision": revision, "source_seals": "source-seals.json"}
HOST_SESSION = {
    "schema_version": 1, "session_id": SESSION_ID, "surface": "copilot-app", "host_version": None,
    "work_map": WORK_MAP, "profile_ref": REFERENCE,
    "bindings": {"browser": {"tool": "explicit Chromium CDP via local Node WebSocket",
                             "available": True, "permission": "allowed"}},
    "isolation": {"kind": "git-worktree", "attributable": True,
                  "evidence": "Explicit current isolated P11 source worktree; not a security sandbox."},
}
(RUN / "shared-context.json").write_text(json.dumps({
    "context": CONTEXT, "work": WORK_IDENTITY, "required_policy": POLICY,
    "host_selection": resolve(load_registry(), HOST_SESSION),
}, indent=2), encoding="utf-8")


def control(kind: str, status: str, observation: dict, evidence: str) -> dict:
    return {"id": f"a16-{kind}", "kind": kind, "requirement": "mandatory",
            "applicability": "applicable", "status": status,
            "reason": "A16 synthetic fixture observation; no independent review claimed.",
            "policy": {"source": ".claude/plans/universal-implementation/packages/P11.md",
                       "version": revision, "applicability": "Selected browser-only A16 acceptance.",
                       "jurisdiction": None, "actor": None, "effective_date": None},
            "evidence": [evidence], "observation": observation}


class SharedContractTests(unittest.TestCase):
    def test_selected_original_work_and_profile_identity_survive_fresh_reader(self):
        self.assertEqual(WORK.load_work_map(ROOT, Path(WORK_MAP))["status"], "APPROVED")
        fresh = verify_profile_reference(REFERENCE, replace(CONFIG, context_id=""))
        self.assertEqual(profile_reference(fresh), REFERENCE)
        self.assertEqual(resolve(load_registry(), HOST_SESSION)["profile_ref"], REFERENCE)
        command([
            sys.executable, str(ROOT / "lib/profile_context.py"),
            "--source", str(ROOT), "--repo", str(ROOT), "--home", str(LINTEL),
            "--packs", str(LINTEL / "packs"), "--pointer", str(LINTEL / "packs/active-pack"),
            "--reference", json.dumps(REFERENCE), "verify",
        ], "fresh-profile-reader")
        self.assertEqual(json.loads((RUN / "fresh-profile-reader.log").read_text(encoding="utf-8")), REFERENCE)

    def test_declared_host_binding_is_not_execution_and_denial_has_no_bypass(self):
        selected = resolve(load_registry(), HOST_SESSION)
        self.assertFalse(selected["executed"])
        self.assertEqual(selected["operations"]["browser"]["mode"], "native")
        denied = json.loads(json.dumps(HOST_SESSION))
        denied["bindings"]["browser"]["permission"] = "denied"
        self.assertEqual(resolve(load_registry(), denied)["operations"]["browser"]["mode"], "blocked")

    def test_missing_browser_and_low_contrast_do_not_become_green(self):
        evidence = (RUN / "shared-context.json").relative_to(ROOT).as_posix()
        browser = control("browser", "pass", {"tool": "unavailable", "executed": False, "states": []}, evidence)
        browser["advisory_score"] = 100
        result = evaluate_controls([browser], required_policy=POLICY)
        self.assertTrue(result["blockers"])
        contrast = control("contrast", "pass", {"ratio": 3.5, "text_size": "normal"}, evidence)
        result = evaluate_controls([contrast], required_policy=POLICY)
        self.assertTrue(result["blockers"])
        self.assertEqual(result["controls"][0]["effective_status"], "fail")

    def test_required_profile_drift_blocks_instead_of_rebinding_browser_context(self):
        target = RUN / "profile-target"
        (target / ".claude").mkdir(parents=True)
        pack = LINTEL / "packs/synthetic-a16"
        pack.mkdir()
        manifest = pack / "pack.yaml"
        manifest.write_text("name: synthetic-a16\nversion: 1.0.0\nextends: _default\n", encoding="utf-8")
        (target / ".claude/profile-requirements.json").write_text(
            '{"schema_version":1,"required_pack":"synthetic-a16"}', encoding="utf-8")
        config = replace(CONFIG, repo=target, context_id="synthetic-a16-required-negative")
        reference = profile_reference(bootstrap_profile_context(config))
        manifest.write_text("name: synthetic-a16\nversion: 1.0.1\nextends: _default\n", encoding="utf-8")
        with self.assertRaisesRegex(ProfileError, "changed|drift"):
            verify_profile_reference(reference, config)
        self.assertEqual(reference["generation"], 1)


PAGE = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>A16 Synthetic Preview</title><link rel="icon" href="data:,">
<style>
*{box-sizing:border-box}body{font:18px/1.5 Arial,sans-serif;color:#172b4d;background:#fff;margin:40px}
main{max-width:740px;margin:auto}h1{font-size:34px;margin-bottom:8px}
label{display:block}input{font:inherit;border:1px solid #52657c;padding:8px}
button{font:inherit;background:#172b4d;color:white;border:0;border-radius:4px;padding:10px 16px;margin:12px 8px 12px 0}
#result{font-weight:bold;font-size:28px}#low-contrast{color:rgb(137,137,137);background:rgb(255,255,255);font-size:16px}
.print-only{display:none}#motion{width:24px;height:24px;background:#236278;animation:pulse 1s infinite}
@keyframes pulse{50%{opacity:.4}}@media(prefers-reduced-motion:reduce){#motion{animation:none}}
@page{size:A4;margin:18mm}@media print{body{margin:0}.controls,#low-contrast,#motion,.screen-only{display:none}
.print-only{display:block}.second{break-before:page}h1{font-size:24pt}}
</style><main><h1>A16 Synthetic Preview</h1><p>Owned local browser operations. No customer data.</p>
<div class="controls"><label for="name">Synthetic name</label><input id="name" value="">
<button id="increment">Increment</button><button id="popup">Refused popup</button>
<label for="password">Unavailable credential input</label><input id="password" type="password"></div>
<p>Count: <span id="result">0</span></p><p>Fixture price: <span id="price">$99.50</span></p>
<ul id="features"><li>Owned session</li><li>Checked redirects</li><li>Real print</li></ul>
<p id="low-contrast">Deliberately low-contrast normal text for a failing mandatory control.</p>
<div id="motion" aria-label="Reduced-motion probe"></div>
<p class="print-only" id="print-summary">Print summary: 0</p>
<section class="print-only second"><h2>A16 second printed page</h2><p>Print-only continuation remains readable.</p></section>
</main><script>
let count=0;
console.log('A16 synthetic ready');
document.querySelector('#increment').addEventListener('click',()=>{
 count++;document.querySelector('#result').textContent=String(count);
 document.querySelector('#price').textContent='$'+(99.5+count).toFixed(2);
 document.querySelector('#print-summary').textContent='Print summary: '+count;
});
document.querySelector('#popup').addEventListener('click',()=>window.open(TRAP_URL));
</script></html>"""


class Fixture:
    def __init__(self):
        self.requests = []
        self.trap_requests = []
        self.proxy_requests = []
        self.health_observed = False
        self.proxy_health_observed = False
        owner = self

        class Trap(BaseHTTPRequestHandler):
            def do_GET(self):
                owner.trap_requests.append(self.path)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"synthetic denied destination")

            def log_message(self, *_):
                pass

        self.trap = ThreadingHTTPServer(("127.0.0.1", 0), Trap)
        self.trap_origin = f"http://127.0.0.1:{self.trap.server_port}"

        class DenyProxy(BaseHTTPRequestHandler):
            def refuse(self):
                try:
                    parsed = urlsplit("//" + self.path if self.command == "CONNECT" else self.path)
                    hostname, port = parsed.hostname, parsed.port
                except ValueError:
                    hostname, port = "invalid-authority", None
                owner.proxy_requests.append({"method": self.command, "hostname": hostname,
                                             "port": port, "status": 403, "forwarded": False})
                self.send_response(403)
                self.send_header("Content-Length", "0")
                self.send_header("Connection", "close")
                self.end_headers()
                self.close_connection = True

            do_GET = refuse
            do_POST = refuse
            do_HEAD = refuse
            do_CONNECT = refuse

            def log_message(self, *_):
                pass

        self.proxy = ThreadingHTTPServer(("127.0.0.1", 0), DenyProxy)
        self.proxy_origin = f"http://127.0.0.1:{self.proxy.server_port}"

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                owner.requests.append({"path": self.path, "authorization_supplied": bool(self.headers.get("Authorization"))})
                redirects = {"/start": "/next", "/next": "/page", "/redirect-chain": "/foreign-redirect",
                             "/foreign-redirect": f"http://localhost:{owner.trap.server_port}/forbidden",
                             "/loop-a": "/loop-b", "/loop-b": "/loop-a"}
                if self.path in redirects:
                    self.send_response(302)
                    self.send_header("Location", redirects[self.path])
                    self.end_headers()
                    return
                if self.path == "/basic-auth":
                    self.send_response(401)
                    self.send_header("WWW-Authenticate", 'Basic realm="synthetic"')
                    self.end_headers()
                    return
                body = b"healthy"
                if self.path == "/page":
                    body = PAGE.replace("TRAP_URL", json.dumps(owner.trap_origin + "/popup")).encode()
                elif self.path == "/script-redirect":
                    body = f"<script>location.href={json.dumps(owner.trap_origin + '/script')};</script>".encode()
                elif self.path == "/foreign-image":
                    body = f'<h1>Subresource test</h1><img src="{owner.trap_origin}/image">'.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.origin = f"http://127.0.0.1:{self.server.server_port}"
        self.servers = (self.server, self.trap, self.proxy)
        self.threads = [threading.Thread(target=server.serve_forever, name=f"a16-{server.server_port}")
                        for server in self.servers]

    def __enter__(self):
        for thread in self.threads:
            thread.start()
        try:
            with build_opener(ProxyHandler({})).open(self.origin + "/health", timeout=5) as response:
                if response.status != 200 or response.read() != b"healthy":
                    raise RuntimeError("Owned fixture server did not respond")
                self.health_observed = True
            try:
                build_opener(ProxyHandler({})).open(self.proxy_origin + "/health", timeout=5)
            except HTTPError as error:
                if error.code != 403:
                    raise
                error.close()
                self.proxy_health_observed = True
            if not self.proxy_health_observed:
                raise RuntimeError("Deny-only proxy did not return its refusal before browser launch")
        except Exception:
            self.__exit__()
            raise
        return self

    def __exit__(self, *_):
        for server, thread in zip(self.servers, self.threads):
            if thread.is_alive():
                server.shutdown()
            server.server_close()
        for thread in self.threads:
            thread.join(timeout=5)
            if thread.is_alive():
                raise RuntimeError("Owned fixture server did not stop")
        (RUN / "server-lifecycle.json").write_text(json.dumps({
            "owner_pid": os.getpid(), "origin": self.origin, "trap_origin": self.trap_origin,
            "health_observed": self.health_observed, "requests": self.requests,
            "trap_requests": self.trap_requests, "deny_proxy": self.proxy_origin,
            "deny_proxy_health_observed": self.proxy_health_observed,
            "proxy_requests": self.proxy_requests, "proxy_forwarding": False,
            "egress_scope": "Observed child-process proxy refusals only; not OS-wide confinement.",
            "credentials_observed": any(x["authorization_supplied"] for x in self.requests),
            "stopped": True,
        }, indent=2), encoding="utf-8")


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(color):
        components = [int(x) / 255 for x in re.findall(r"\d+", color)]
        if len(components) != 3:
            raise AssertionError("Fixture requires measured opaque RGB colors")
        linear = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in components]
        return sum(x * y for x, y in zip(linear, (0.2126, 0.7152, 0.0722)))
    values = sorted((luminance(foreground), luminance(background)))
    return (values[1] + 0.05) / (values[0] + 0.05)


def live(node: str) -> None:
    if OPTIONS.browser is None or not OPTIONS.browser.is_absolute():
        raise AssertionError("--live needs an explicitly selected absolute --browser executable")
    verify_profile_reference(REFERENCE, CONFIG)
    with Fixture() as fixture:
        request = RUN / "live-input.json"
        request.write_text(json.dumps({"origin": fixture.origin, "trapOrigin": fixture.trap_origin,
                                      "denyProxy": fixture.proxy_origin,
                                      "executable": str(OPTIONS.browser), "outputRoot": str(RUN),
                                      "context": CONTEXT}, indent=2), encoding="utf-8")
        command([node, str(ROOT / "tests/integration/browser-live.mjs"), str(request)], "live-browser")
        if fixture.trap_requests:
            raise AssertionError(f"Unauthorized synthetic destination was contacted: {fixture.trap_requests}")
        if any(x["authorization_supplied"] for x in fixture.requests):
            raise AssertionError("A credential-bearing request was sent")
    results = json.loads((RUN / "live-results.json").read_text(encoding="utf-8"))
    if results["context"] != CONTEXT or results["outcome"] != "pass" or len(results["cases"]) != 8:
        raise AssertionError("Incomplete or changed live browser evidence")
    happy = results["cases"][0]["result"]
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        raise AssertionError("PDF text/layout observation unavailable: pdftotext missing")
    pdf = happy["pdf"]
    text_path = RUN / "printed-text.txt"
    bbox_path = RUN / "printed-bounds.html"
    command([pdftotext, "-layout", "-enc", "UTF-8", pdf, str(text_path)], "print-text")
    command([pdftotext, "-bbox", pdf, str(bbox_path)], "print-bounds")
    text = text_path.read_text(encoding="utf-8")
    for expected in ("A16 Synthetic Preview", "Print summary: 2", "A16 second printed page",
                     "Print-only continuation remains readable."):
        if expected not in text:
            raise AssertionError(f"Actual printed PDF lacks {expected!r}")
    if "Unavailable credential input" in text or "Deliberately low-contrast" in text:
        raise AssertionError("Print CSS failed to hide screen-only controls")
    tree = ET.parse(bbox_path)
    pages = tree.findall(".//{http://www.w3.org/1999/xhtml}page")
    if len(pages) != 2:
        raise AssertionError(f"Expected two actual printed pages, observed {len(pages)}")
    words = 0
    for page in pages:
        width, height = float(page.attrib["width"]), float(page.attrib["height"])
        for word in page.findall(".//{http://www.w3.org/1999/xhtml}word"):
            words += 1
            if not (0 <= float(word.attrib["xMin"]) < float(word.attrib["xMax"]) <= width
                    and 0 <= float(word.attrib["yMin"]) < float(word.attrib["yMax"]) <= height):
                raise AssertionError("Printed text extends outside a page")
    if not words:
        raise AssertionError("No actual printed words were observed")
    element = happy["contrast"]["elements"][0]
    ratio = contrast_ratio(element["color"], element["background"])
    evidence = (RUN / "live-results.json").relative_to(ROOT).as_posix()
    observed = control("browser", "pass", {
        "tool": "Chromium CDP through Node built-in WebSocket",
        "executed": True,
        "states": ["local page read", "mouse click and keyboard Enter changed count to 2",
                   "reduced motion disabled animation", "screen and print-media screenshots captured",
                   "Page.printToPDF produced two text-inspected pages", "foreign requests refused",
                   "fresh owned contexts disposed and browser processes exited"],
    }, evidence)
    measured = control("contrast", "pass", {"ratio": ratio, "text_size": "normal"}, evidence)
    browser_outcome = evaluate_controls([observed], required_policy=POLICY)
    negative = evaluate_controls([observed, measured], required_policy=POLICY)
    if browser_outcome["blockers"] or not negative["blockers"]:
        raise AssertionError("Shared P05 result semantics were lost")
    verify_profile_reference(REFERENCE, CONFIG)
    (RUN / "live-controls.json").write_text(json.dumps({
        "browser": browser_outcome, "deliberate_low_contrast_negative": negative,
        "print": {"pages": len(pages), "words_within_page": words, "text": str(text_path),
                  "bounds": str(bbox_path), "pdf": pdf, "print_media": happy["printMedia"],
                  "pdf_raster_visual_inspection": "not_run; separate from print-media screenshot"},
        "visual_review": "pending; inspect screen.png and print-media.png separately",
        "profile_reference_preserved": REFERENCE,
    }, indent=2), encoding="utf-8")


def main() -> int:
    print(f"Owned evidence: {RUN}", flush=True)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SharedContractTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    node = shutil.which("node")
    if not node:
        raise AssertionError("Node unavailable; browser adapter contract tests were not executed")
    command([node, "--test", "--test-reporter=tap", str(ROOT / "tests/integration/browser-operations.test.mjs")],
            "browser-contracts")
    tests = (RUN / "browser-contracts.log").read_text(encoding="utf-8")
    counts = {name: int(re.search(rf"^# {name} (\d+)$", tests, re.MULTILINE).group(1))
              for name in ("tests", "pass", "fail", "skipped")}
    if counts["tests"] == 0 or counts["fail"] or counts["skipped"]:
        raise AssertionError("Zero, failed or skipped contracts cannot establish acceptance")
    if OPTIONS.live:
        live(node)
    if seal() != SEALS:
        raise AssertionError("Source changed during browser verification")
    summary = {"source_revision": revision, "shared_contract_tests": result.testsRun,
               "node_contracts": counts, "browser": "observed" if OPTIONS.live else "not_run",
               "source_seals_unchanged": True, "work_map": WORK_MAP, "profile_ref": REFERENCE}
    (RUN / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
