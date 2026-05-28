---
name: scrape
layer: foundation
description: Extract structured data from one or more pages — declarative selector schema, JSON output.
color: green
tools: Read, Bash, Glob
voice: internal
cli_support: [claude-code]
---

# /scrape

Bulk-extraction sibling of `/browse`. Given a list of URLs + a selector schema, returns structured JSON. Use for research, dataset construction, documentation harvesting — within ToS limits.

Distinct from `/browse`: that one is interactive single-page. This is declarative multi-page.

## When to use

- Build a small dataset from public docs (e.g. extract code examples from a tutorial site)
- Harvest a vendor's pricing/feature matrix for a `/plan-ceo-review` comparison
- Compare wording across multiple URLs (e.g. "how does each competitor describe X")
- Periodic monitoring (with `--diff` against a prior run)

## When NOT to use

- Single page, exploratory — use `/browse`
- Behind auth — set up via `/setup-browser-cookies` first OR consider that the ToS may forbid scraping
- High-volume commercial scraping — out of scope. Lintel is a builder's toolbox, not a scraping platform.
- Customer data, even sanitized — STOP. Layer 2 blocks.

## Inputs

- Required `--urls <file|inline>` — list of URLs, one per line
- Required `--schema <yaml>` — declarative extraction spec (selectors → field names)
- Optional `--concurrency <N>` — parallel page loads (default: 3, max: 10)
- Optional `--rate-limit <ms>` — minimum delay between requests to the same host (default: 1000ms)
- Optional `--diff <prior.json>` — diff this run against a prior JSON output

## Workflow

1. **Validate schema.** Parse the selector YAML, confirm each rule has `field` + `selector` + optional `transform`.
2. **Compliance gate.** Resolve each URL's hostname. Block any in `~/.lintel/compliance/prod-hosts.txt`. Warn on hosts whose `robots.txt` disallows the path.
3. **Fetch loop.** For each URL: load via Playwright (handles JS-rendered content), apply selectors, transform, accumulate.
4. **Rate-limit.** Respect `--rate-limit` per-hostname. If multiple URLs share a host, queue them serially.
5. **Output.** JSON file at `~/.lintel/scrape-runs/<ts>/results.json`. Failure entries are emitted (with error) — never silently dropped.
6. **Optional diff.** If `--diff`: produce a structured diff (added/removed/changed records).

## Schema format

```yaml
# scrape-schema.yaml
fields:
  - name: title
    selector: 'h1.product-title'
    transform: trim
  - name: price
    selector: '.price-tag'
    transform: number_extract  # strips currency, returns numeric
  - name: features
    selector: 'ul.features li'
    multi: true
    transform: trim
```

## Report format

```
Scrape: 12 URLs, schema=product-catalog.yaml

Concurrency: 3
Rate limit: 1000ms/host
Duration: 28s
Success: 11
Failure: 1

## Failures
- https://vendor3.example.com/missing — 404 (not retried, exit on first 4xx)

## Sample record (first)
{"url": "https://vendor1.example.com/x", "title": "Widget X", "price": 99.0, "features": ["Auto-sync", "API access", "Free tier"]}

## Diff vs prior run
Added: 2 records
Removed: 1 record
Changed: 3 records (prices moved on widget-Y, widget-Z, widget-Q)

Output: ~/.lintel/scrape-runs/20260527-161033/results.json
```

## Compliance integration

- Layer 2 customer-data gate applies per-URL.
- `robots.txt` checked on first visit per host. Disallowed paths surface as warnings — not auto-blocked (operator owns the ToS judgment), but logged to audit.
- Rate-limit enforced to avoid hammering target sites. Default 1s/host is conservative.
- Per-call auth required if any URL hostname matches `~/.lintel/compliance/auth-required-hosts.txt`.

## Voice tier note

`voice: internal`. Scrape reports are engineering-internal — counts and paths, no narrative.

## Failure modes

- **Schema YAML invalid:** parse error with line:col + bail before any fetch.
- **Selector matches 0 elements on a page:** emit the record with empty field, log the miss. Do not retry.
- **Host rate-limit triggered (429):** back off exponentially, retry once. If second 429: skip remaining URLs for that host, continue with other hosts.
- **`robots.txt` disallow + operator did NOT pass `--ignore-robots`:** skip the URL, report it in failures, do not crash the whole run.
- **Concurrency > 10:** refuse — Lintel does not facilitate aggressive scraping.

## Examples

**Tiny dataset:**
```
> /scrape --urls vendors.txt --schema product-catalog.yaml
✓ 12/12 success, results.json 8KB
```

**With diff:**
```
> /scrape --urls vendors.txt --schema product-catalog.yaml --diff prior.json
✓ 11/12 success. Diff: 2 added, 1 removed, 3 changed prices.
```

**Failed schema:**
```
> /scrape --urls vendors.txt --schema bad.yaml
✗ Schema invalid at bad.yaml:14 — `selector` required, found `selecter` (typo).
```

## See also

- `/browse` — single-page interactive
- `/make-pdf` — when output should be PDF not JSON
- `/setup-browser-cookies` — for auth-required scrape targets
- Layer 2 compliance — robots.txt and ToS judgment
