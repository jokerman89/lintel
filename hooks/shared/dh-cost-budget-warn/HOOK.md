---
name: dh-cost-budget-warn
tier: warn-only
event: PreCommit on IaC files
fires_on: commit increases projected cloud cost above pack/profile threshold (heuristic: scaling-up SKU class, adding always-on resource, increasing replica count beyond cap)
override: pass --ignore-cost-warn flag (operator decision, logged)
audit: ~/.lintel/audit/hooks.jsonl
---

# dh-cost-budget-warn

Surfaces IaC commits that bump cost without explicit acknowledgment. Warning, not block — cost increases are sometimes correct (scaling up for ramp); operator decides.

## What it does

- Detects IaC files (Terraform, Helm, Kubernetes manifests, Bicep)
- Scans for cost-increasing patterns:
  - SKU upsizing (e.g. `Standard_D2s_v3` → `Standard_D8s_v3`)
  - Replica increases (`replicas: 1` → `replicas: 10`)
  - Always-on additions (new persistent disk, premium SKU storage)
  - Removed cost guards (autoscaling min → max increase)
- If pattern detected: WARN with the change + suggest cost-projection refresh

## Why warn-only

- Cost ramp-ups are sometimes deliberate (customer ramp, peak preparation)
- Block would interrupt legitimate scaling
- Warn prompts operator to confirm + refresh projection

## Override path

`--ignore-cost-warn "reason"` on commit. Reason logged.

## Audit format

```jsonl
{"hook":"dh-cost-budget-warn","tier":"warn","ts":"...","file_edited":"infra/main.tf","patterns":"sku-upsize,replicas-up","operator":"<operator>"}
```
