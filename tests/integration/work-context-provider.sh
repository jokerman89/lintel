#!/usr/bin/env bash
# component: work-context-provider-tests
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P08.md
# constraints: accepted mechanical providers only; semantic workflow review remains separate
# last_intent_review: 2026-09-22
# tag: integration universal lifecycle
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python="${LINTEL_PYTHON:-python3}"
PYTHONDONTWRITEBYTECODE=1 "$python" "$root/tests/integration/universal-work-lifecycle.py" --root "$root" \
  WorkSelectionTests.test_named_swarm_singleton_uses_selected_coordination_without_acceptance \
  WorkSelectionTests.test_selected_coordination_is_counted_once_and_cannot_switch_initiatives \
  WorkSelectionTests.test_ordinary_heading_does_not_become_a_task_without_explicit_selection \
  WorkSelectionTests.test_explicit_map_original_ids_and_no_writes \
  WorkSelectionTests.test_manifest_measures_selected_and_warming_bytes_once \
  WorkSelectionTests.test_budget_matches_reported_capacity_boundary_without_a_default_cap \
  WorkSelectionTests.test_binding_uses_p05_and_original_mapped_task_progress \
  WorkSelectionTests.test_missing_selected_artifact_not_hidden_by_other_initiative \
  WorkSelectionTests.test_real_profile_and_map_survive_fresh_shell_resume \
  WorkSelectionTests.test_profile_bound_inspection_cannot_override_target_or_map \
  WorkSelectionTests.test_required_profile_drift_blocks_resume_before_output \
  WorkSelectionTests.test_cold_resume_does_not_recreate_missing_profile \
  WorkSelectionTests.test_two_initiatives_resume_and_append_to_original_history \
  WorkSelectionTests.test_analysis_pointer_and_binding_ignore_stale_global_report \
  LifecycleTests.test_cycle_identity_cannot_be_overridden_by_metadata \
  LifecycleTests.test_footer_uses_status_not_next_metadata \
  LifecycleTests.test_cycle_close_preserves_segment_and_old_cycle \
  LifecycleTests.test_begin_once_and_interrupted_resume \
  LifecycleRecoveryTests.test_truncated_done_transition_stays_incomplete \
  LifecycleRecoveryTests.test_operator_metadata_cannot_forge_a_completed_phase \
  LifecycleRecoveryTests.test_cycle_read_error_cannot_become_a_fresh_start \
  LifecycleRecoveryTests.test_resume_ignores_metadata_and_retains_loop_back \
  LifecycleRecoveryTests.test_failed_state_write_and_field_injection_are_errors \
  LifecycleRecoveryTests.test_selected_phase_range_never_duplicates_entry \
  LifecycleRecoveryTests.test_resume_uses_selected_range_not_a_phase_default_hint \
  "$@"
