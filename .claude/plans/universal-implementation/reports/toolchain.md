# Local validation toolchain evidence

2026-09-20. This records development tooling, not a product dependency or client acceptance.

The chosen prerequisite check `bash -c 'jq --version'` failed with exit 127: jq absent.
That absence had also left jq-only assertions unexecuted in the profile lane. The existing
test documentation already requires jq for strict release verification.

A task-local jq 1.8.2 Windows AMD64 binary was obtained from the official jqlang/jq
release using anonymous HTTPS with curl configuration disabled. No account, token,
customer data or source code was sent. The downloaded binary and checksum manifest
matched the release API's SHA-256 values before the executable was used:

| Artifact | SHA-256 |
|---|---|
| jq-windows-amd64.exe | `a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627` |
| sha256sum.txt | `dc86824a41c165ece971ff691aff6e08bbfe6e1d1f531688b47ee78c283a85cd` |

Sources: [binary](https://github.com/jqlang/jq/releases/download/jq-1.8.2/jq-windows-amd64.exe)
and [checksums](https://github.com/jqlang/jq/releases/download/jq-1.8.2/sha256sum.txt).
Executable location is gitignored `.claude/runtime/tools/jq-1.8.2/jq.exe` in the
MasterSession worktree; the binary is not committed or bundled into consumer projects.
Version execution returned `jq-1.8.2`. No global PATH/configuration/registry change was made.

Each test process must explicitly prepend this directory to PATH; shell environment does
not persist between tool calls. Re-run affected required assertions instead of treating a
previous skipped assertion as passing. No Linux/macOS or alternative jq version is claimed
by this receipt. The provenance registry's optional yq listing remains unexecuted; its
actual YAML and declared local paths were checked separately.
