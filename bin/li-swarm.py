#!/usr/bin/env python3
# component: swarm-cli
# implements: ADR-0026, ADR-0027
# intent: docs/concepts/swarming-work.md
# constraints: read-only; standard library only; never executes artifact content
# last_intent_review: 2026-09-22
"""Read-only validation and evidence gates for a Lintel swarm."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from profile_context import ProfileConfig

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(ROOT / "lib"))

from swarm_contract import (  # noqa: E402
    Diagnostic,
    ValidationResult,
    brief_payload,
    check_lane_scope,
    git_changed_paths,
    inspect_local,
    inspect_local_frontier,
    local_lane_states,
    lane_states,
    package_sources,
    ready_frontier,
    review_input,
    snapshot_lane,
    SwarmContractError,
    validate_coordination,
    verify_close,
)


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="working repository root")
    parser.add_argument("--coord", required=True, help="repository-relative coordination.json path")
    parser.add_argument("--profile-home", type=Path)
    parser.add_argument("--profile-packs", type=Path)
    parser.add_argument("--profile-pointer", type=Path)
    parser.add_argument("--profile-context-file", type=Path)


def _emit(result: ValidationResult, **payload: object) -> int:
    output = result.as_dict()
    output.update(payload)
    print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if result.ok else 1


def _changed_paths(args: argparse.Namespace) -> list[str]:
    paths = list(args.changed or [])
    if args.paths_file:
        if args.paths_file == "-":
            content = sys.stdin.read()
        else:
            content = Path(args.paths_file).read_text(encoding="utf-8-sig")
        paths.extend(line for line in content.splitlines() if line != "")
    return paths


def _selected_work(args: argparse.Namespace, contract: dict[str, Any]) -> dict[str, Any]:
    # The trusted reader calls Swarm validation; compose here, never in its library.
    reader = runpy.run_path(str(ROOT / "bin/li-work-artifacts.py"))
    root = args.repo.resolve()
    selected = args.work_map if args.work_map is not None else Path(contract["work_map"])
    work = reader["work_context"](root, selected)
    mapped = reader["artifact_path"](root, contract["work_map"]).relative_to(root).as_posix()
    if work["work_map"] != mapped:
        raise ValueError("Selected work map differs from the explicit coordination backpointer")
    packages = package_sources(root, contract)
    for lane in contract["lanes"]:
        task_id = lane["task_id"]
        if work["packages"].get(task_id) != packages[task_id]:
            raise ValueError(f"Selected original package/leaf identity differs for lane {task_id}")
    return work


_RESUME_SCRIPT = r'''
set -euo pipefail
audit_log() {
  printf 'lintel-swarm resume diagnostic (not-persisted):' >&2
  printf ' %q' "$@" >&2
  printf '\n' >&2
}
source "$LINTEL_SOURCE_ROOT/lib/workflow.sh"
workflow_resume "$1" "$2"
'''


def _resume_context(
    args: argparse.Namespace, work: dict[str, Any], config: ProfileConfig,
) -> tuple[dict[str, Any], ProfileConfig]:
    from profile_context import required_policy, verify_profile_reference
    from review_contract import load_json

    if not args.cycle_id.strip():
        raise ValueError("--cycle-id must select a nonempty original cycle")
    environment = {key: value for key, value in os.environ.items() if not key.startswith("BASH_FUNC_")}
    for key in (
        "BASH_ENV", "ENV", "PACK_CACHE_FILE", "LINTEL_CYCLE_ID", "LINTEL_WORK_MAP",
        "LINTEL_PROFILE_CONTEXT", "LINTEL_PROFILE_CONTEXT_FILE", "LINTEL_PROFILE_REFERENCE",
        "LINTEL_PROFILE_PACK", "LINTEL_REQUIRED_POLICY",
    ):
        environment.pop(key, None)
    environment.update(
        LINTEL_SOURCE_ROOT=ROOT.as_posix(), LINTEL_REPO_ROOT=config.repo.as_posix(),
        LINTEL_PYTHON=Path(sys.executable).as_posix(),
        _LINTEL_PROFILE_PYTHON=Path(sys.executable).as_posix(),
        LINTEL_HOME=config.home.as_posix(), LINTEL_PACKS_DIR=config.packs.as_posix(),
        LINTEL_ACTIVE_PACK_FILE=config.pointer.as_posix(), PYTHONDONTWRITEBYTECODE="1",
    )
    if config.context_file is not None:
        environment["LINTEL_PROFILE_CONTEXT_FILE"] = config.context_file.as_posix()
    if args.state_dir is not None:
        environment["LINTEL_STATE_DIR"] = (config.repo / args.state_dir).as_posix()
    observed = subprocess.run(
        [shutil.which("bash") or "bash", "--noprofile", "--norc", "-s", "--", args.cycle_id, work["work_map"]],
        input=_RESUME_SCRIPT, cwd=config.repo, env=environment,
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if observed.stderr:
        sys.stderr.write(observed.stderr)
    observed.check_returncode()
    recovered = load_json(observed.stdout)
    if (
        recovered["cycle_id"] != args.cycle_id or recovered["work_map"] != work["work_map"]
        or recovered["artifacts"] != work["artifacts"] or recovered["release_clearance"] is not False
    ):
        raise ValueError("Resumed cycle differs from the explicitly selected original work")
    live = verify_profile_reference(recovered["profile"], config)
    if required_policy(live) != recovered["required_policy"]:
        raise ValueError("Resumed cycle required policy differs from the live selected profile")
    bound = replace(config, context_id=recovered["profile"]["context_id"],
                    expected_reference=recovered["profile"])
    return {"mode": "persisted-cycle", **recovered}, bound


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate topology and ownership")
    _common(validate_parser)

    wave_parser = subparsers.add_parser("wave", help="show the next evidence-aware ready frontier")
    _common(wave_parser)
    wave_parser.add_argument("--host-capability", choices=("native", "sequenced", "none"), help="caller-observed capacity; never grants host permissions")

    resume_parser = subparsers.add_parser("resume", help="reconstruct candidate work and pending review from committed artifacts")
    _common(resume_parser)
    resume_parser.add_argument("--host-capability", choices=("native", "sequenced", "none"))
    resume_parser.add_argument("--cycle-id", help="verify this original persisted cycle before shared consumption")
    resume_parser.add_argument("--state-dir", type=Path, help="explicit existing state directory for --cycle-id")

    status_parser = subparsers.add_parser("status", help="show lane evidence states")
    _common(status_parser)

    verify_parser = subparsers.add_parser("verify", help="fail unless every lane has complete independent evidence")
    _common(verify_parser)
    for accepting_parser in (wave_parser, resume_parser, status_parser, verify_parser):
        accepting_parser.add_argument("--map", dest="work_map", type=Path,
                                      help="explicit work map; must agree with --coord (defaults to its backpointer)")
    inspect_parser = subparsers.add_parser("inspect", help="retain local observation inspection without shared acceptance")
    _common(inspect_parser)
    inspect_parser.add_argument("--check-complete", action="store_true", help="require all local reports/reviews, still not shared clearance")

    scope_parser = subparsers.add_parser("check-scope", help="validate one attributable lane change set")
    _common(scope_parser)
    scope_parser.add_argument("--task", required=True, help="lane task_id")
    scope_parser.add_argument("--actor", choices=("worker", "reviewer"), default="worker", help="whose attributable change set is being checked")
    scope_parser.add_argument("--changed", action="append", help="one repository-relative changed path; repeat as needed")
    scope_parser.add_argument("--paths-file", help="newline-delimited paths, or - for stdin")
    scope_parser.add_argument("--base", help="derive actual changed paths from this local Git commit")
    scope_parser.add_argument("--head", help="derive actual changed paths through this local Git commit")

    snapshot_parser = subparsers.add_parser("snapshot", help="capture work/acceptance/result identity without creating review evidence")
    _common(snapshot_parser)
    snapshot_parser.add_argument("--task", required=True)
    snapshot_parser.add_argument("--attempt", required=True)
    snapshot_parser.add_argument("--base", help="local Git base commit; use with --head")
    snapshot_parser.add_argument("--head", help="local Git result commit; use with --base")
    brief_parser = subparsers.add_parser("brief", help="emit a structured brief payload retaining the original Markdown as data")
    _common(brief_parser)
    brief_parser.add_argument("--task", required=True)
    review_parser = subparsers.add_parser("review-input", help="export exact report/result binding for a real reviewer; never creates PASS")
    _common(review_parser)
    review_parser.add_argument("--task", required=True)

    args = parser.parse_args()
    try:
        config = None
        locations = (args.profile_home, args.profile_packs, args.profile_pointer)
        if any(value is not None for value in locations) or args.profile_context_file is not None:
            if any(value is None for value in locations):
                raise ValueError("Explicit --profile-home, --profile-packs and --profile-pointer are required together")
            from profile_context import ProfileConfig
            config = ProfileConfig(
                source=ROOT, repo=args.repo, home=args.profile_home, packs=args.profile_packs,
                pointer=args.profile_pointer, context_file=args.profile_context_file,
            )
        if args.command == "validate":
            result = validate_coordination(args.repo, args.coord)
            return _emit(result)
        metadata: dict[str, object] = {}
        if args.command in ("status", "wave", "resume", "verify"):
            result = validate_coordination(args.repo, args.coord)
            if not result.ok or result.contract is None:
                return _emit(result, release_clearance=False)
            try:
                work = _selected_work(args, result.contract)
                metadata["work_context"] = work
            except (ImportError, OSError, ValueError) as error:
                result.diagnostics.append(Diagnostic("error", "work.selection", "work_map", str(error)))
                return _emit(result, release_clearance=False)
            if args.command == "resume":
                metadata["recovery"] = {"mode": "artifact-only", "release_clearance": False}
                try:
                    if args.state_dir is not None and args.cycle_id is None:
                        raise ValueError("--state-dir requires an explicit --cycle-id")
                    if args.cycle_id is not None:
                        if config is None:
                            raise ValueError("Persisted-cycle resume requires the three explicit profile locations")
                        metadata["recovery"], config = _resume_context(args, work, config)
                except subprocess.CalledProcessError as error:
                    result.diagnostics.append(Diagnostic(
                        "error", "work.resume", "cycle_id", f"workflow_resume failed with exit {error.returncode}",
                    ))
                    _emit(result, release_clearance=False)
                    return error.returncode
                except (ImportError, OSError, ValueError) as error:
                    result.diagnostics.append(Diagnostic("error", "work.resume", "cycle_id", str(error)))
                    return _emit(result, release_clearance=False)
        if args.command in ("wave", "resume"):
            result, frontier = ready_frontier(args.repo, args.coord, host_capability=args.host_capability, profile_config=config)
            return _emit(result, frontier=frontier, verification="shared_evidence", release_clearance=False, **metadata)
        if args.command == "status":
            states = []
            if result.ok and result.contract is not None:
                states, evidence = lane_states(args.repo, result.contract, coordination_path=args.coord, profile_config=config)
                result.diagnostics.extend(evidence)
            return _emit(result, lanes=states, verification="shared_evidence", release_clearance=False, **metadata)
        if args.command == "verify":
            result, states = verify_close(args.repo, args.coord, profile_config=config)
            return _emit(result, lanes=states, verification="shared_evidence", release_clearance=False, **metadata)
        if args.command == "inspect":
            if args.check_complete:
                result, states = inspect_local(args.repo, args.coord)
            else:
                result = validate_coordination(args.repo, args.coord)
                states = []
                if result.ok and result.contract is not None:
                    states, diagnostics = local_lane_states(args.repo, result.contract)
                    result.diagnostics.extend(diagnostics)
            _, frontier = inspect_local_frontier(args.repo, args.coord)
            return _emit(result, lanes=states, frontier=frontier, verification="local_observations_only", release_clearance=False)
        if args.command == "check-scope":
            paths = _changed_paths(args)
            if args.base or args.head:
                if paths or not (args.base and args.head):
                    raise ValueError("Use both --base/--head or an explicit path list, not both")
                paths = git_changed_paths(args.repo, args.base, args.head)
            result = check_lane_scope(args.repo, args.coord, args.task, paths, actor=args.actor)
            return _emit(result, task_id=args.task)
        if args.command == "snapshot":
            snapshot = snapshot_lane(args.repo, args.coord, args.task, args.attempt, base=args.base, head=args.head)
            return _emit(ValidationResult(), snapshot=snapshot, verification="local_observations_only", release_clearance=False)
        if args.command == "brief":
            print(json.dumps(brief_payload(args.repo, args.coord, args.task), indent=2, ensure_ascii=True))
            return 0
        if args.command == "review-input":
            return _emit(ValidationResult(), review_input=review_input(args.repo, args.coord, args.task))
    except SwarmContractError as error:
        return _emit(ValidationResult(diagnostics=error.diagnostics))
    except (OSError, ValueError, UnicodeError) as error:
        print(json.dumps({"ok": False, "diagnostics": [{"severity": "error", "code": "io", "path": "", "message": str(error)}]}, indent=2), file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
