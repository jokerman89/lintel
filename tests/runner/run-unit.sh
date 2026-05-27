#!/usr/bin/env bash
# Convenience wrapper: run unit tests only.
exec bash "$(dirname "${BASH_SOURCE[0]}")/run-all.sh" --scope unit "$@"
