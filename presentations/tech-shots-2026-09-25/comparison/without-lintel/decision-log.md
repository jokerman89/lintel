# Decision log

1. **One derived view.** Validate fixture records once, normalize a separate UTC date value without modifying window.TICKETS, then compute a single matching array for each filter change. Metrics, graphs, results and export consume that array. This prevents conflicting counts.
2. **Dependency-free local files.** Classic script tags load tickets.js and app.js alongside index.html, with styles.css for presentation. No imports, fetch, fonts or remote resources are needed for file:// launch.
3. **UTC throughout.** Date filters and grouping use new Date(createdAt).toISOString().slice(0, 10). Table display explicitly labels UTC, while CSV preserves each original createdAt string.
4. **Text and CSV boundaries.** Build dynamic elements with textContent. CSV fields are always quoted, embedded quotes doubled and leading formula-like text prefixed with an apostrophe, including prefixes after whitespace. This intentionally changes dangerous export cells for spreadsheet safety.
5. **Accessible charts and narrow screens.** Visible day/count labels accompany vertical bars. Status labels and counts accompany a proportional breakdown. Native controls have explicit labels, focus outlines and error descriptions. Ticket table rows become labelled cards on mobile.
6. **Error handling.** Invalid input yields a descriptive alert and zero derived outputs; invalid source data disables export. Valid zero matches keep a header-only export available.
7. **Scope honesty.** This synthetic pilot provides neither authentication nor tenant isolation. Production requires server-side authorization and data isolation. No network, installs or deployment are used.
