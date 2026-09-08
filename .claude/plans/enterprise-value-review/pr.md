Company profiles could lose inherited controls or return empty hook lists, and the planning
workflow repeated execution and review setup for every small task. This change preserves
effective enterprise requirements and applies the approved hybrid plan: short tasks with
individual evidence, executed and reviewed in coherent work packages.

The shared pack reader now handles the documented scalar/list/nested subset consistently,
checks inherited requirements and rejects invalid ancestry. Team creation retains parent
policy, risk routing consumes list values, and session digests show the loaded identity.
Plans connect applicable company requirements to work IDs, acceptance and evidence; estimates
state their basis without multiplying a whole-cycle prior by the number of leaves.

Validation: 93/93 scripts passed in the aggregate run, with focused final parser/cache and
workflow regressions recorded in the review report. Independent pack implementation and
hybrid scenario reviews closed their findings. Internal jq assertions still need CI; no
private company profile, live hook registration or measured productivity pilot was tested.
Manifest JSON/version parity and Bash syntax passed. `install/verify.sh --all` returned 0;
its missing-yq skip and existing legacy-count diagnostic are documented in the review.
After isolating the commits onto main, all eight targeted pack, scale and integration
scripts passed again. The 93-script aggregate result is from the original inspected base.

The review used baseline `6b10a84`; its commits were isolated onto main `9a024c0` for this PR,
excluding two earlier unpublished commits. Reconcile overlapping Copilot changes before
combining them. The review records two pre-existing P1 Git collection defects
(F05/F06); this PR does not establish readiness as an enterprise enforcement layer.

The operator approved the documented M2 exception for draft-PR publication on 2026-09-08.
The mechanical RED and rollout limitations remain recorded. See the manual compatibility
disposition and `.claude/engineering/audits/2026-09-08-enterprise-value-review.md` for evidence,
remaining findings and rollout steps. Version 0.10.0 is unreleased.

Integration status at publication: Copilot PR #83 merged into main while this draft was
being published. GitHub reports conflicts with the updated base. Reconcile the overlapping
runtime, planning, documentation and release metadata before merge, then validate the
combined tree. The tests above describe this review branch; no combined-tree CI pass is claimed.
