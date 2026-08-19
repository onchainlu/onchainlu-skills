---
name: smells
description: Review the current branch or working-tree diff for real bugs, security and data-integrity risks, reliability failures, and scalability regressions; then propose and fix confirmed issues. Use for $smells, /smells, code-smells reviews, deep diff reviews, or requests to find substantive risks in changed code. Use the separate clean skill for cleanup-only requests.
---

# Smells

Review changed code rigorously, focusing on failures that matter in production. Keep the review grounded in the diff and the repository's own conventions.

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
7. Invoke the separate `clean` skill over the final diff. If cleanup changes
   code, rerun the relevant verification.

## Review Rules

- Treat the user and repository conventions as authoritative.
- Prefer demonstrated risks over theoretical ones; identify no issue when none is substantiated.
- Protect security, money, user data, and service availability first.
- Fix rather than lecture, while preserving user control over material edits.
- End with a compact summary of findings, accepted fixes, verification, and any remaining risks.
