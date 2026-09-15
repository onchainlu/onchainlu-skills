---
name: session-handoff
description: Capture the current repository state, confirmed decisions, open questions, and next steps in a concise resume note before stopping or switching work. Use when the user asks to hand off a session, preserve context, wrap up work, or prepare a later continuation.
---

# Session Handoff

Create a concise, evidence-backed snapshot that lets the next session resume
without reconstructing the work from scratch. This is the counterpart to a
context-resume workflow.

## Gather the current state

Inspect the repository before drafting anything:

- Recent commits for the session (default: the last eight hours; use a user-specified period when given).
- `git diff --stat`, `git status --short`, and `git stash list`.
- Open or recently updated pull requests when the forge CLI is authenticated.
- Planning or status documents changed during the session, when the repository has them.

Report observed facts separately from inferences. Do not expose secrets or
session data, and do not write, commit, push, or change remote state while
gathering evidence.

If uncommitted work exists, call it out clearly in the handoff and ask whether
the user wants it committed. Leave it untouched unless they explicitly ask for
a commit.

## Confirm human context

Ask only for details that cannot be recovered from the repository:

1. Key decisions and their rationale.
2. Open questions or blockers.
3. The first useful action for the next session.

Do not invent decisions, ownership, approvals, or completed verification. If
the user does not provide an answer, record it as not supplied rather than
blocking the handoff.

## Surface optional follow-ups

Briefly identify any durable learnings, changelog gaps, or stale planning work
that the session evidence supports. Propose those separately; do not write
notes, lessons, changelog entries, archive files, or delete anything without
explicit user approval.

## Write the resume note

Before writing, use the repository's established handoff or continuation
location and format when one exists. Otherwise, ask the user where the note
should live. Never place a handoff note in a public repository if it would
contain private paths, customer material, credentials, or personal session
context.

Use this structure, adapting it to the repository's conventions:

```markdown
# Context Resume: <project>

**Session date:** YYYY-MM-DD
**Branch:** <branch>

## What happened

- <observed commits, pull requests, and status changes>

## Decisions made

- <user-confirmed decisions, or "Not supplied">

## Open questions

- <user-confirmed blockers, or "None identified">

## Next steps

- <user-confirmed next action>

## Working state

- Branch: <branch>
- Uncommitted: <yes/no and affected files>
- Stashes: <count>
- Open pull requests: <list or none found>
```

After writing, report the exact path and the outstanding work. The resume note
is a current snapshot, not a historical log; update or replace it on the next
handoff rather than appending stale state.
