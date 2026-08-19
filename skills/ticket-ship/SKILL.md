---
name: ticket-ship
description: >-
  Take a tracker ticket through to shipped: find or start the PR, drive it to
  mergeable, update the ticket state, draft the stakeholder message. Use for
  Jira/Linear (or acli) tickets assigned to you.
---

# Ticket → Ship

The ticket-shaped parts of shipping. The PR mechanics live in their own skills —
this is what a tracker adds on top.

## GitHub authentication

Before asking the user to log in again, run `gh auth status -h github.com`. If
that check ran without network access or inside a restricted sandbox, repeat
the same read-only check in a network-capable context and treat that result as
authoritative. Never print token values. Request login only once and only when
the authoritative check fails; report missing administrative scope separately
from authentication failure.

## Steps

1. Read the ticket and list the assigned work (`acli`, Jira, Linear, etc.).
2. Confirm the correct base branch(es) before starting — some orgs need a
   release branch plus the default (`stacked-pr`). Never assume; verify the
   org's rule.
3. Find the existing PR or start one (`work` → `pr-update`), then drive it
   mergeable (`pr-ready`) and polish before handoff (`clean`).
4. Move the ticket to the right state (In Review / Test / whatever this tracker
   uses). Link the PR on the ticket.
5. Draft the stakeholder update — Slack or a ticket comment, short, `no-tropes`.
   Don't send it unless asked.

## Don't

- Assume the base branch.
- Mark the ticket done while CI is red or review threads are open.
- Let the ticket and the PR tell different stories about the state of the work.
