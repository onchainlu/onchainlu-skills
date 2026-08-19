---
name: smells
description: Review the current branch or working-tree diff for real bugs, security and data-integrity risks, reliability failures, and scalability regressions; then propose and fix confirmed issues. Also polish the diff with KISS/DRY and local style when the user asks for /clean, "clean it up", "tidy this", or a pre-PR cleanup. Use the deep review workflow for $smells or code-smells asks and the lightweight cleanup workflow for /clean asks.
---

# Smells and Clean

Review changed code rigorously, focusing on failures that matter in production. Keep the review grounded in the diff and the repository's own conventions.

## Choose the mode

- **`/smells`**: run the full review workflow below, report substantive findings, fix confirmed issues, and verify the result.
- **`/clean`**: run only the cleanup workflow below. Polish the code by hand; do not turn cleanup into a full review or test-suite run.

The standalone `clean` skill packages the same cleanup workflow so `/clean` is independently discoverable on every surface.

Run cleanup automatically at the end of every `/smells` review and before creating, updating, or automerging a PR, unless the user or repository workflow says otherwise.

## Cleanup workflow (`/clean`)

1. Re-read the current branch or working-tree diff.
2. Remove dead code, leftover debug logging, needless ceremony, and duplication.
3. Extend existing helpers instead of parallel-implementing them.
4. Match neighboring names, imports, file layout, comments, and abstractions.
5. Prefer the smallest clear implementation. Avoid unrelated refactors, new one-caller abstractions, and scope creep.
6. Treat cleanup as polish, not validation. Run a targeted check only when it is genuinely needed to confirm the cleanup is safe; do not run the full test suite, typecheck, or lint merely because the user said `/clean`.
7. For a PR handoff, keep the title and body focused on the change as a whole, not a changelog of steps.
8. Report what changed and which checks ran. Call out any substantive bug for a deeper review instead of expanding this cleanup pass.

## Review workflow (`/smells`)

1. Identify the review target.
   - Prefer the diff from the current branch's merge-base with `main` or `master`.
   - If no branch diff is available, review staged and unstaged working-tree changes.
   - Stop and say so if there is no changed code to review.

2. Build enough context to judge the change.
   - Read every changed file in full, its immediate callers/importers where relevant, and the applicable repository instructions and configuration.
   - Note whether each affected path is hot (frequent/runtime-critical), warm (user-facing or recurring), or cold (rare/admin/background).

3. Review only issues meaningfully connected to the diff. Look for:
   - broken logic, incorrect state transitions, edge cases, regressions, and unsafe assumptions;
   - missing validation, error handling, cancellation, cleanup, timeouts, bounded retries, concurrency controls, and idempotency;
   - security or data-integrity exposure, including authorization boundaries, unsafe filesystem or network access, secret handling, injection, SSRF, and cross-tenant data access;
   - scalability risks such as unbounded work, N+1 calls, fan-out, repeated expensive work, cache stampedes, blocking paths, and missing database indexes when query shape changes;
   - mismatch with established repository patterns, tests, types, APIs, or observability.

   Think through realistic failure modes and high load, but do not manufacture speculative findings.

4. Report findings before editing, grouped by file and severity:
   - **Critical** — likely security breach, data loss/corruption, outage, or broad correctness failure.
   - **Warning** — plausible reliability, correctness, performance, or maintainability regression.
   - **Nit** — small local improvement with negligible production impact.

   For each finding, give the location, concise evidence, why it fails, and the smallest safe repair. Do not pad the report with generic style advice.

5. Fix confirmed Critical and Warning findings in severity order.
   - Present the proposed repair and request approval before each material change unless the user has explicitly asked for autonomous fixes.
   - Keep changes minimal and localized. Do not refactor unrelated code or expand scope beyond the diff.
   - Follow existing repository patterns rather than introducing a new architecture.

6. Verify the result using the repository's own relevant formatter, lint, typecheck, test, or build commands. State what ran and any limitations.
7. Run the Cleanup workflow above over the final diff. If cleanup changes code, rerun the relevant verification.

## Review Rules

- Treat the user and repository conventions as authoritative.
- Prefer demonstrated risks over theoretical ones; identify no issue when none is substantiated.
- Protect security, money, user data, and service availability first.
- Fix rather than lecture, while preserving user control over material edits.
- End with a compact summary of findings, accepted fixes, verification, and any remaining risks.
