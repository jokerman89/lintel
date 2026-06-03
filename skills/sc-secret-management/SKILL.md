---
name: sc-secret-management
layer: foundation
description: SC sub-skill — secret inventory + rotation policy + secret-scan integration. Dispatches to SecurityAuditor + SBOMAuditor agents.
color: red
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are SC-SECRET-MANAGEMENT — the workflow that produces a secret inventory and rotation policy.

## What this skill does

Enumerates secrets the system uses (env vars, KeyVault refs, embedded credentials, OAuth tokens, signing keys, encryption keys). Spawns `SecurityAuditor` for classification + rotation policy and `SBOMAuditor` for dependency-secret detection (secrets shipped by libraries). Raises help when a secret has no rotation path.

## When to use

- SC full pass secrets_inventoried checkpoint
- Single action `/li:sc single --action secret-management`
- New integration introduces credentials
- Compliance audit prep
- Pre-rotation policy review

## When NOT to use

- Single-secret rotation (use secret-manager directly)
- Already-managed secrets without inventory gap

## Workflow

### Step 1 — Read preferences + existing inventory

```bash
secret_management="${secret_management:-local-encrypted}"   # keyvault | aws-secrets-manager | hashicorp-vault | local-encrypted

existing_inventory=".lintel/state/sc/secret-inventory.md"
[ -f "$existing_inventory" ] && has_prior=true || has_prior=false
```

### Step 2 — Spawn SecurityAuditor for enumeration + classification

```bash
brief_file=$(mktemp)
cat > "$brief_file" <<EOF
task: Enumerate all secrets the system depends on + classify by kind
context_pointers:
  - $existing_inventory (if present)
  - environment configs / .env files (if present)
  - infrastructure-as-code files
constraints:
  - per secret: name, kind (api-key | oauth-token | signing-key | encryption-key | password | webhook-secret),
    scope (per-environment | per-tenant | global), current storage location,
    proposed storage location: ${secret_management}, rotation_cadence_days
  - flag secrets without rotation path
acceptance:
  - structured inventory with per-secret kind + scope + storage + rotation
EOF

/li:brief-forge subagent_spawn sc-secret-management SecurityAuditor brief "$brief_file"
```

### Step 3 — Spawn SBOMAuditor for dependency-secret detection

```bash
sbom_brief=$(mktemp)
cat > "$sbom_brief" <<EOF
task: Identify secrets that ship with dependencies (default tokens, demo keys, embedded credentials)
context_pointers:
  - dependency manifests (package.json / go.mod / requirements.txt / etc.)
  - .lintel/state/sc/secret-inventory.json
constraints:
  - flag any dependency with known-default credentials
  - flag any lockfile with hex strings that look like secrets
acceptance:
  - per-dependency: clean | suspect | confirmed-default-credential
EOF

/li:brief-forge subagent_spawn sc-secret-management SBOMAuditor brief "$sbom_brief"
```

### Step 4 — Raise-help if no-rotation secrets exist

```bash
no_rotation=$(jq -r '.secrets[] | select(.rotation_cadence_days == null) | .name' .lintel/state/sc/secret-inventory.json 2>/dev/null | wc -l)
if [ "$no_rotation" -gt 0 ]; then
  echo "RAISE_HELP: $no_rotation secret(s) without rotation path"
fi
```

### Step 5 — Audit + emit

```bash
ts=$(date -u +"%Y%m%dT%H%M%SZ")
out=".lintel/state/sc/secret-inventory-$ts.md"
{
  echo "# Secret inventory — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Target store: $secret_management"
  echo ""
  echo "## Inventory"
  cat .lintel/state/sc/secret-inventory.md
  echo ""
  echo "## Dependency secrets"
  cat .lintel/state/sc/sbom-secrets.md
} > "$out"

printf '{"ts":"%s","kind":"sc_secret_management","secrets":%d,"no_rotation":%d,"target_store":"%s","operator":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$secret_count" "$no_rotation" "$secret_management" "$(whoami 2>/dev/null || echo unknown)" \
  >> "$LINTEL_HOME/audit/sc-decisions.jsonl"
```

## Status protocol

- **DONE** — inventory emitted, every secret has rotation path
- **DONE_WITH_CONCERNS** — emitted with 1-2 dependency-suspect findings
- **BLOCKED** — raise-help triggered (no-rotation secrets)

## Integration

**Reads:** env configs, IaC files, dependency manifests
**Writes:** `.lintel/state/sc/secret-inventory-<ts>.md`, audit JSONL
**Dispatches to:** SecurityAuditor (enumeration), SBOMAuditor (dependency secrets)

## Anti-patterns

- **Hardcoding secret_management** — read profile
- **Inventory without rotation policy** — every secret has a rotation cadence
- **Skipping dependency secrets** — supply-chain leaks happen
- **Curating secret patterns** — agents detect, this skill orchestrates (L-001)
