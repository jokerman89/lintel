#!/usr/bin/env bash
# Convenience wrapper: run e2e tests only.
exec bash "$(dirname "${BASH_SOURCE[0]}")/run-all.sh" --scope e2e "$@"
