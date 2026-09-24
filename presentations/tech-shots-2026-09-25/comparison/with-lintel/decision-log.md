# Decision log

1. Use static HTML/CSS and plain browser JavaScript. Required offline launch rules out network dependencies. Alternatives: a bundled framework adds build machinery; a server conflicts with direct-file launch. Chosen approach is proportionate to twelve synthetic records.
2. Derive one filtered array each render and use it for metrics, graphs, table and export. This directly implements the stakeholder reconciliation requirement.
3. Normalize valid timestamps to UTC dates for filtering/grouping while retaining originals for CSV. Prevents offset-boundary disagreement.
4. Create text nodes for all fixture values. Quote every CSV cell and apostrophe-prefix whitespace/formula-leading values. Preserve original fixtures unchanged.
5. Represent a reversed date range as an invalid view with explanatory feedback and zero results. The user can correct dates or clear filters; export is disabled only for invalid/data-error views.
6. Keep this local pilot honest: no authentication or isolation claim, no external assets, no telemetry. No global ADR or lesson is promoted. These are local decisions; no operator correction occurred.
