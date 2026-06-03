---
name: context-warm-from-url
layer: foundation
description: Fetch URL + dump into context. Useful for loading documentation, blog posts, external references on-demand.
color: cyan
tools: Read, Bash, WebFetch
voice: internal
cli_support: [claude-code, codex]
---

You are the context-warm-from-url skill.

## What this skill does

Fetches a URL via WebFetch and dumps content into session context. When the active pack's compliance mode is `hard`, validates the URL against the pack's approved-domain allowlist (none by default).

## When to use

- Loading a documentation page for current discussion
- Bringing in a referenced blog post for design comparison
- Fetching a specific gist or GitHub README

## When NOT to use

- Untrusted URLs (pack compliance gate blocks when mode is `hard`)
- Already in context (don't re-fetch)
- Long-running data fetch (not for live API calls — those are subagent or tool work)

## Workflow

### Step 1 — URL validation

```bash
url="$1"

# Validate format
if ! echo "$url" | grep -qE '^https?://'; then
  echo "Invalid URL: $url"
  exit 1
fi

# Compliance check (only enforced when the active pack runs in hard mode)
compliance_mode=$(resolve_pack_field compliance.mode)   # advisory by default
if [ "$compliance_mode" = "hard" ]; then
  # Allowed domains come from the active pack's allowlist (empty by default)
  mapfile -t allowed_domains < <(resolve_pack_field compliance.url_allowlist 2>/dev/null)

  domain=$(echo "$url" | sed -E 's|https?://([^/]+).*|\1|')
  is_allowed=no
  for allowed in "${allowed_domains[@]}"; do
    [ -z "$allowed" ] && continue
    [[ "$domain" == "$allowed" || "$domain" == *.${allowed#*.} ]] && { is_allowed=yes; break; }
  done

  if [ "$is_allowed" = "no" ]; then
    # Ask operator
    echo "URL not in the pack's approved-domain allowlist. Confirm or cancel?"
    # AskUserQuestion: A) load anyway / B) cancel
  fi
fi
```

### Step 2 — WebFetch with prompt

```bash
# Use WebFetch tool, asking for full content
content=$(WebFetch url="$url" prompt="Return the full content of this page, preserving structure (headings, lists, code blocks). Be exhaustive — no summarizing.")
```

### Step 3 — Estimate + load

Approximate token cost. If >20k: ask confirm.

Load into session context via Read-equivalent injection.

### Step 4 — 00-state.md + audit log

```yaml
event: context_warm_from_url
url: <url>
domain: <domain>
compliance_check: <pass/skipped>
tokens_added: <approx>
ts: <timestamp>
```

Audit log for compliance trail: `~/.lintel/audit/url-fetches.jsonl`.

## Status protocol

- DONE / BLOCKED (URL invalid OR pack compliance gate denied)

## Pause-points

- Off-allowlist domain confirmation (if the active pack's compliance mode is `hard`)

## Hop-in support

YES.

## Integration

Reads via WebFetch tool. Writes audit log.

## Anti-patterns

- **Bypassing the pack compliance URL check** — never
- **Fetching same URL repeatedly** — check 15-min cache via WebFetch
- **Loading URLs that don't actually contain text** (binaries, paywalled, JS-rendered) — surface failure cleanly

## Voice tier behavior

`voice: internal`.
