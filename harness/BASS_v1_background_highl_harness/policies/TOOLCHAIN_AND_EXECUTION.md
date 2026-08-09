# Toolchain and execution policy

No uploaded executable/script is trusted merely because its archive is structurally safe.
Dependency installation, build scripts, procedural macros, Python imports, tests, CAS
notebooks, and shell bootstrap files are code execution and require an authorized phase.

Use a project-local isolated Python environment and a pinned Rust toolchain selected from
the canonical source's MSRV/toolchain contract. Never use system `pip`,
`--break-system-packages`, ambient `LD_LIBRARY_PATH`, wildcard wheel installation, or
unlocked network builds. Separate dependency intake/audit from offline build/test.

Rust 1.94.1 may be used only when the owner confirms it as an exact reproduction target.
Reverify official SHA-256 and GPG signature immediately before bounded installation into
an explicit workspace-owned prefix. The uploaded Rust-core archive is a historical partial
overlay until mapped to a canonical commit; never extract it over user code.
