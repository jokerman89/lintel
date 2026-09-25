# Pack defaults: a validated neutral baseline

**Last updated:** 2026-09-20

`packs/_default/pack.yaml` is the company-neutral baseline. It lets a first-time
operator use Lintel without a company pack, global configuration or private data.
It is data that must load and validate, not a set of hardcoded emergency values.

The current manifest supplies internal voice, advisory compliance, no company
control hooks, no brand/corpus/role paths, the ordinary `cycle` workflow, disabled
external capture and extension awareness, and generic handoff evaluator settings.
The manifest is the field reference; this page does not maintain a competing copy.
Control/extension declarations alone never prove execution or install hooks.

## Two legitimate uses

With no selected profile, the resolver loads valid `_default`. For another valid
pack, it supplies only missing optional fields. Declaring a child block replaces
the parent's whole block; neutral field defaults are not deep inheritance from
that parent. Explicit null/false/empty/list values remain explicit.

A pack can also explicitly `extends: _default` when it wants ordinary inheritance.
Every manifest still declares its own identity. See [inheritance](pack-inheritance.md).

## Failure is not first use

Repository `.claude/profile-requirements.json` or explicit `LINTEL_PROFILE_PACK`
selection makes policy required before its manifest is read. Missing, malformed
or incompatible required policy cannot become advisory success.

Only a legacy optional active-pack preference can fall back after a failed load,
with `OPTIONAL_PROFILE_FALLBACK` and an explicit recorded fallback status. An invalid
neutral baseline is an error, even when the requested pack is optional. Once bound,
changed inputs block until explicit rebind/replan, rather than silently falling back.
[ADR-0029](../../.claude/decisions/0029-required-profile-context.md) records this
intentional change from the old emergency-success cache.

## Authoring and compatibility

Create a separate named pack for team policy instead of editing the shipped neutral
manifest. An explicitly configured local `_default` override still participates in
normal source precedence and validation; its content is pinned like any other source.
`lib/pack-schema.yaml` declares schema-1 and resolver feature contracts independently
of public product versions. Historical `requires_lintel: ">=4.0.0"` is a legacy
pack-v1 marker, not a demand for current public v4.

Frozen-zone changes need compatibility and shape evidence. The extension shape test,
fallback/inheritance tests and Universal profile-context integration test cover the
neutral and failure boundaries. Passing them does not certify a live company profile,
host policy enforcement, client discovery or a renderer.
