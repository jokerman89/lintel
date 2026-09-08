#!/usr/bin/env bash
# component: jobs-registry-concurrency-test
# implements: ADR-0005
# intent: docs/concepts/jobs-system.md
# constraints: all writers and registry files live in a temporary home
# last_intent_review: 2026-09-08
set -euo pipefail
review_source="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
review_parent="$(cd "${TMPDIR:-/tmp}" && pwd -P)"
review_tmp="$(mktemp -d "$review_parent/lintel-registry.XXXXXX")"
trap 'case "$review_tmp" in "$review_parent"/lintel-registry.*) rm -rf -- "$review_tmp" ;; esac' EXIT
export LINTEL_HOME="$review_tmp/home" LINTEL_JOBS_NO_INIT=1
export LINTEL_JOBS_REGISTRY="$LINTEL_HOME/jobs/_active.md"
source "$review_source/bin/_jobs.sh"

# Start all writers at the same barrier; they must preserve each other's scope.
pids=""
for n in 1 2 3 4 5 6; do
  mkdir -p "$review_tmp/scope$n/job$n"
  printf 'job_id: job%s\nworkflow: cycle\nstatus: ACTIVE\ncurrent_step: BUILD\n' "$n" > "$review_tmp/scope$n/job$n/job.yaml"
  (
    export LINTEL_JOBS_DIR="$review_tmp/scope$n"
    while [ ! -f "$review_tmp/start" ]; do sleep 0.05; done
    _registry_sync "scope$n"
  ) &
  pids="$pids $!"
done
touch "$review_tmp/start"
for pid in $pids; do wait "$pid"; done
[ "$(grep -c '^-' "$LINTEL_JOBS_REGISTRY")" = 6 ]
for n in 1 2 3 4 5 6; do grep -Fq "<!-- repo:scope$n -->" "$LINTEL_JOBS_REGISTRY"; done
echo 'PASS: concurrent writers preserve all six repository scopes'

# Updating an emptied scope removes only that scope, including after concurrent writes.
mkdir -p "$review_tmp/empty"
LINTEL_JOBS_DIR="$review_tmp/empty" _registry_sync scope3
[ "$(grep -c '^-' "$LINTEL_JOBS_REGISTRY")" = 5 ]
! grep -Fq '<!-- repo:scope3 -->' "$LINTEL_JOBS_REGISTRY"
echo 'PASS: removing a scope preserves every other job'

cp "$LINTEL_JOBS_REGISTRY" "$review_tmp/before"
mkdir "$LINTEL_JOBS_REGISTRY.lock"
if LINTEL_REGISTRY_LOCK_ATTEMPTS=1 _registry_sync blocked 2>"$review_tmp/error"; then
  echo 'FAIL: contended registry reported success'; exit 1
fi
cmp "$review_tmp/before" "$LINTEL_JOBS_REGISTRY"
grep -q 'registry sync unavailable' "$review_tmp/error"
[ -d "$LINTEL_JOBS_REGISTRY.lock" ]
rmdir "$LINTEL_JOBS_REGISTRY.lock"
echo 'PASS: lock timeout preserves the registry and never steals the lock'

# Read errors are not an empty/legacy registry and may never replace old bytes.
for reader in grep awk; do
  if (
    if [ "$reader" = grep ]; then
      grep() { return 2; }
    else
      awk() { return 2; }
    fi
    LINTEL_JOBS_DIR="$review_tmp/empty" _registry_sync broken
  ) 2>"$review_tmp/error"; then
    echo "FAIL: $reader read error reported success"; exit 1
  fi
  cmp "$review_tmp/before" "$LINTEL_JOBS_REGISTRY"
  [ ! -d "$LINTEL_JOBS_REGISTRY.lock" ]
  [ -z "$(find "$(dirname "$LINTEL_JOBS_REGISTRY")" -name '_active.md.tmp.*')" ]
done
echo 'PASS: registry read failures preserve other scopes and release temporary state'
