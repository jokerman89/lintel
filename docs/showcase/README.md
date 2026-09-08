# Showcase

[`lintel-the-harness.html`](lintel-the-harness.html) is a generated, self-contained system map.
Open it in a browser; it needs no build step. Use the [getting-started guide](../getting-started.md)
for adoption and the [skill catalog](../../skills/CATALOG.md) for the canonical inventory.

## What the page represents

The page combines repository-derived counts with a short system map and architecture overview.
It is a snapshot of its generation source, not proof that every catalog item runs on every client.
The [Copilot guide](../copilot.md) defines native integration scope, and
[enterprise adoption](../enterprise-adoption.md) defines the evidence needed for a rollout.

## Open it

```powershell
Invoke-Item docs\showcase\lintel-the-harness.html
```

On macOS, use `open docs/showcase/lintel-the-harness.html`; on Linux, use your browser or
`xdg-open docs/showcase/lintel-the-harness.html`.

## Regenerate through the source

```bash
bash bin/li-wiki-gen --showcase-only
bash bin/li-wiki-gen --check
```

`bin/li-wiki-gen` and `lib/wiki-gen.sh` own the generated copy and layout. Hand edits to the HTML
are overwritten. Source changes must be regenerated and reviewed before release. The check
reports drift against the repository; it does not verify runtime behavior.

The output embeds its styling and requires no external assets. Hyperlinks navigate to the
referenced documentation when opened. See [wiki generation](../concepts/wiki-generation.md)
for sources, determinism and verification.
