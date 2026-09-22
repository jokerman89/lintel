# A20.1/A20.2 - Accurate reuse records

Implementer: MasterSession; base `40c2795`. Independent P13 acceptance pending.

The installer and declaration registry incorrectly claimed all content was
operator-authored despite existing design-dna attribution and retained MIT/Apache notices.
The correction distinguishes reference declarations from already distributed adaptations,
records known release/unknown import commits and separately records pinned audit
comparison revisions. Existing notices and specialist source content are unchanged.

The historical similarity proposal is preserved with an explicit superseded-guidance
banner. Lexical rewriting is not an originality, licensing or quality gate. Public
provenance guidance now links actual component attribution/notices and requires exact
component/revision/modification records for future updates.

No third-party source was imported or executed, no license text rewritten, no private
material exported, and no remote operation performed. A20.3/4 compatibility belongs to P07
and remains separate; A20 is not complete from these documentation corrections.

Verification: the installed YAML parser read the registry; both adapted-component
records resolve every declared local path, attribution and notice, and all eight original
reference entries remain. The existing `install/verify.sh --upstream` returned zero but
explicitly skipped its listing because yq is absent; that listing is not claimed as
executed evidence. `git diff --check` passed. No dependency was installed for this slice.
