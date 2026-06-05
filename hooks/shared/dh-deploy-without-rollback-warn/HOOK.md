---
name: dh-deploy-without-rollback-warn
tier: warn-only
event: PreCommit on deploy/IaC files
fires_on: commit touches deploy manifest, helm chart, Terraform, or CI/CD pipeline file without rollback declaration in same commit or in .lintel/state/dh/rollback-strategy-*.md
override: pass --ignore-rollback flag (operator decision, logged)
audit: ~/.lintel/audit/hooks.jsonl
---

# dh-deploy-without-rollback-warn

Surfaces when a deploy or IaC commit lacks a documented rollback path. Warning, not block — some deploys are deliberately one-way; operator decides.

## What it does

- Detects deploy/IaC commits via path heuristic + `pack.devops_hosting.deploy_path_glob`
- Checks for paired rollback declaration in same commit OR latest `rollback-strategy-*.md` in `.lintel/state/dh/`
- If no rollback declared: WARN

## Why warn-only

- Some deploys are deliberately one-way (data deletes, account closures)
- Operator may have legitimate reason to defer rollback docs
- Block would be too aggressive for routine deploys

## Override path

`--ignore-rollback "reason"` on commit. Reason logged.

## Audit format

```jsonl
{"hook":"dh-deploy-without-rollback-warn","tier":"warn","ts":"...","file_edited":"infra/k8s/deployment.yaml","rollback_age_days":-1,"operator":"<operator>"}
```
