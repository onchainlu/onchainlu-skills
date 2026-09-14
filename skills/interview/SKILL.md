---
name: interview
description: Interview the user one question at a time to turn a product, feature, system, workflow, or other implementation problem into a complete, reviewable plan. Use for requirements discovery and implementation planning; do not use for job-interview preparation.
---

# Interview

Turn the user's initial problem statement and source material into an execution-ready plan without beginning implementation.

## Operating contract

- Treat this as discovery and planning only. Reading supplied documents, inspecting relevant workspace state, and writing the final plan are allowed; implementation is not.
- Read the material the user supplied before asking questions. Inspect relevant code, documentation, configuration, and current state when the answers are already available there.
- Preserve provenance. Separate facts found in source material, user decisions, recommendations, and assumptions.
- Ask exactly one primary question per turn. Do not hide several decisions inside a compound question or send a questionnaire.
- Choose the next question by information value: resolve the uncertainty most likely to change scope, architecture, user experience, risk, or acceptance criteria.
- Do not ask the user for information that can be learned safely from the provided material or workspace.
- When the user may not know the answer, briefly give two or three concrete options, recommend one with a reason, and ask them to choose or delegate the decision.
- If an answer conflicts with earlier material or a prior decision, surface the conflict and resolve it before moving on.
- Accept "skip," "unknown," or "decide for me." Make a reasonable recommendation, record it as an assumption or delegated decision, and continue unless the choice is material and unsafe to infer.
- Keep each turn concise. Summarize accumulated understanding only at a meaningful checkpoint or when confirmation would prevent rework.

## Discovery

Adapt the sequence to the problem rather than following a fixed questionnaire. Start broad enough to establish the intended outcome, then narrow into the parts that affect implementation. Cover the applicable areas:

- purpose, desired outcome, users, and measures of success
- current behavior, pain points, source-of-truth material, and relevant prior work
- required use cases, user journeys, inputs, outputs, business rules, and edge cases
- explicit in-scope and out-of-scope boundaries
- preferred experience and behavior, including examples or reference products when useful
- system boundaries, data, interfaces, integrations, dependencies, and compatibility needs
- constraints involving technology, time, cost, ownership, policy, or operations
- quality requirements such as security, privacy, reliability, performance, accessibility, and observability
- migration, rollout, rollback, support, documentation, and maintenance expectations
- acceptance criteria and the evidence that will prove the work is complete
- authorization boundaries for implementation, deployment, external changes, and destructive actions

Maintain a working decision ledger while interviewing. Track resolved decisions, evidence, assumptions, open questions, and deferred ideas. Avoid exposing the full ledger on every turn.

## Readiness test

Continue the interview while any unanswered question could materially change the proposed design, scope, sequencing, risk, or definition of done.

The interview is ready to close when:

- the outcome and non-goals are unambiguous;
- the important behavior and edge cases are specified;
- major technical and product choices are decided or have an accepted default;
- dependencies, risks, rollout needs, and authorization boundaries are known;
- acceptance criteria are testable; and
- remaining unknowns are explicitly deferred and do not block planning.

Before writing the final plan, give a compact synthesis of the intended solution and ask one final confirmation question. If the user corrects it, update the ledger and continue discovery as needed.

## Plan document

After confirmation, create a Markdown plan in the relevant workspace. Follow an existing planning-document convention when one exists. Otherwise use a clear descriptive filename in an appropriate `docs/` or planning directory; if there is no workspace, provide the complete document in chat.

Make the document self-contained enough for a new implementation session. Include only applicable sections, covering:

1. status and approval gate
2. problem, purpose, and desired outcome
3. source material and observed current state
4. goals, non-goals, users, and use cases
5. functional behavior and edge cases
6. chosen design and rejected alternatives with brief reasons
7. affected components, data, interfaces, and dependencies
8. ordered implementation phases with concrete changes and checkpoints
9. testing, acceptance criteria, and completion evidence
10. rollout, migration, rollback, observability, and operational ownership
11. risks and mitigations
12. assumptions, deferred work, and any remaining non-blocking questions

Use exact paths, component names, commands, and interfaces when verified. Do not invent details to make the plan look complete. Label inferences and unverified assumptions.

End with an explicit execution checkpoint: summarize what approval would authorize, identify any actions that would still need separate approval, and wait. Do not implement, commit, push, deploy, message external parties, or mutate external systems until the user approves execution after reviewing the plan.
