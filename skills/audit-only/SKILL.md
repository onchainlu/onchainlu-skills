---
name: audit-only
description: >-
  Read-only investigation mode: answer and report findings before any changes.
  Use when the user asks to audit, investigate, diagnose, review, explain current
  state, plan without execution, or explicitly says not to change anything. Do
  not trigger merely because an action request is phrased as a question.
---

# Audit Only

Investigate and report. Do not edit code, create files, or open PRs until the
user explicitly says to proceed.

## Do

1. Read the relevant code/data and answer the actual question first.
2. Report findings: what's there, what's wrong, options + a recommendation.
3. If a change is warranted, describe it and wait for a go.
4. If asked, post findings as a PR/issue comment — that's still not code edits.
5. Treat "can you deploy/fix/update this?" as an action request, not an audit,
   unless the user also limits the task to investigation or planning.

## Don't

- Start writing code because the fix seems obvious.
- Act on assumed scope — answer what was asked, nothing more.
- Treat a request for review, explanation, or status as permission to change
  things.
