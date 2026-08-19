---
name: clean
description: Polish the current branch or working-tree diff by removing dead code, debug leftovers, duplication, and needless ceremony while preserving behavior. Use for /clean, "clean it up", "tidy this", or a pre-PR cleanup; do not perform a full code-smells review unless requested.
---

# Clean

Polish the current diff without expanding its scope.

## Workflow

1. Identify the final branch or working-tree diff and re-read it before editing.
2. Remove dead code, leftover debug logging, needless ceremony, and duplication.
3. Reuse existing helpers and match neighboring names, imports, file layout, comments, and abstractions.
4. Prefer the smallest clear implementation. Avoid unrelated refactors, new one-caller abstractions, and scope creep.
5. Treat cleanup as polish, not validation. Run a targeted check only when it is genuinely needed to confirm the cleanup is safe; do not run the full test suite, typecheck, or lint merely because cleanup was requested.
6. For a PR handoff, keep the title and body focused on the change as a whole, not a changelog of cleanup steps.
7. Report what changed and which checks ran. Call out any substantive bug for a deeper `/smells` review instead of expanding this cleanup pass.

When `/smells` finishes its deep review, apply this same cleanup workflow to the final diff.
