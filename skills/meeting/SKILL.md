---
name: meeting
description: Process a Granola or other meeting transcript into an Obsidian vault, preserving the raw source and extracting durable context and follow-up captures. Use when the user provides a transcript, asks to process a synced meeting, or wants meeting and calendar context incorporated into the vault.
---

# Process Meeting Transcript

1. Confirm the vault root contains `1on1s`, `05-CLAUDE/context`, and `00-INBOX`. If a required directory is missing, stop and ask for the vault path or confirmation to create it. Obtain the transcript, and ask for attendee names or a topic only when neither can be inferred from the transcript.
2. Check whether the raw transcript already exists in `1on1s/` (as it normally will after the Granola sync). Preserve that source; otherwise save it as `lucas <> <people> <topic-or-date>.md` with `created`, `source`, `type: meeting`, and `attendees` frontmatter.
3. Use relevant, read-only calendar context when it is already available through the vault or an authorized connected source. Treat it as planning context, not a substitute for what was actually said in the meeting.
4. Create or update topic or person context files in `05-CLAUDE/context/`. Preserve names, numbers, examples, quotes, decisions, opinions, uncertainty, and speaker attribution; do not flatten them into vague summaries.
5. Create a separate `00-INBOX` capture for each action item, open question, surprising insight, or idea worth developing, using `type: capture` and the transcript source.
6. Report the transcript path, context files changed, capture count, and the meeting's single most important takeaway.

Do not send or publish transcript material unless the user explicitly asks.
