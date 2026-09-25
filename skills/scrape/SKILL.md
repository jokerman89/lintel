---
name: scrape
layer: foundation
description: Use to extract structured data from authorized pages with selector schemas, explicit pacing, visible failures and prior-run comparison.
color: green
tools: Read, Bash, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# /scrape

Declarative multi-page sibling of `/browse`, using the same
[browser operations and ownership](../browse/references/browser-operations.md).
Keep research, documentation harvesting, small datasets and prior-run comparison.
This is not a high-volume scraping platform or permission to collect customer data.

## Inputs

- `--urls <file|inline>`: explicit URLs, one per line; validate all before fetching.
- `--schema <yaml>`: selected data-only selector schema. Use an available YAML
  parser or structured JSON; do not invent a parser or execute transforms as code.
- `--concurrency <N>`: requested page count, default 3 and maximum 10. Each page
  needs attributable ownership and the same admission checks. The delivered
  single-page provider is serial; report effective concurrency 1 and obtain a
  changed choice if concurrency matters, rather than pretending it ran in parallel.
- `--rate-limit <ms>`: minimum interval between request starts per hostname,
  default 1000ms. Browser subresources are not independent scraping jobs.
- `--diff <prior.json>`: selected previous results, read as data without execution.

## Schema and concrete extraction

```yaml
fields:
  - name: title
    selector: h1.product-title
    transform: trim
  - name: price
    selector: .price-tag
    transform: number_extract
  - name: features
    selector: ul.features li
    multi: true
    transform: trim
```

`name` is the field key (the earlier workflow's `field` wording was inconsistent).
Require unique nonempty names and selectors, boolean `multi` when present, and a
known transform. The delivered `scripts/extract.mjs` consumes this **parsed** schema,
uses the same browser's `read` operation, and implements trim, text and
number_extract without evaluating supplied code. Ambiguous numeric strings produce
an explicit field error; do not guess locale/currency or silently emit NaN.
`number_extract` accepts one complete decimal amount, including `.50`, with at most
one ASCII sign before or after an optional currency symbol and an optional
whitespace-separated alphabetic unit/currency label. It preserves the sign; it does
not convert currencies. Grouping/locale separators, exponent notation, accounting
parentheses, multiple amounts and unsupported decoration are explicit field errors,
never partially parsed digit substrings.
Whitespace, signs, the optional currency symbol, digits and trailing label are
consumed by one forward cursor. Invalid whitespace/decorated fields within the
browser's existing read bound do not enter a backtracking regular expression.

## Workflow

1. Validate schema, URL list, requested pacing/concurrency and output ownership
   before opening pages. Carry the same work map and verified P07 reference.
2. Inspect actual browser provider/isolation and apply P03 host, scheme/port and
   redirect admission to pages, robots retrieval and subresources alike.
3. Establish authorized use and the site's terms/robots rules before the batch.
   A disallowed path is skipped with a recorded reason; inaccessible/ambiguous
   rules remain unresolved. Do not auto-invent an `--ignore-robots` permission.
   An explicit permissible exception needs its own documented scope.
4. For authenticated data, follow `/setup-browser-cookies`. Keep the user-chosen
   surface; if it cannot support this extraction, preserve a manual task instead
   of transferring a session or acquiring personal cookies.
5. Schedule the next permitted URL only after the same-host interval. Load with
   `open`, confirm actual status/state, then call `extractPage(browser, schema)`.
   Preserve one result per input, including HTTP, selector, policy and tool errors.
6. A missing single value is null; a missing multi value is an empty list; both
   carry an explicit field error and make that record unsuccessful. A single
   selector matching several elements is ambiguous, not "take the first".
7. Do not retry 4xx errors blindly. For 429, honor a bounded Retry-After/backoff,
   retry once only when authorized, then stop remaining URLs for that host.
   A policy/provider failure closes the affected context; do not continue in a
   partially trusted session. Report unattempted inputs with their blocker.
8. Write JSON under the explicitly owned gitignored run, then use `diffRecords`
   for added/removed/changed URL records. Preserve failed records in comparisons.
   Close owned contexts and servers using their exact handles.

The small extraction/diff module does not launch browsers, parse YAML, schedule
concurrency or claim to enforce robots/ToS. Those are workflow preconditions and
provider observations. State which were actually checked; absent mandatory checks
stay unverified through P05.

## Results

A result contains `url`, `fields`, `errors` and `ok`. Report attempted/succeeded/
failed/unattempted counts, effective concurrency and pacing, schema/source revision,
work/profile identity, actual provider/context, output paths and diff summary.
Do not fabricate duration, robot-policy clearance or success from a JSON file's size.

Keep extracted content within the authorized scope; do not include credentials,
customer data or personal account information in examples or retained artifacts.
For visual verification use `/browse`; for a composed PDF use `/make-pdf`.
