---
name: brief
description: Create a daily reflection from an Obsidian vault using recent captures, synced Granola meetings, available calendar context, and connections. Use when the user asks for a daily brief, connections among recent notes, a weekly pattern, or a question worth considering. Save the result in 03-BRIEFS when operating in a vault.
---

# Daily Vault Brief

1. Confirm that the current directory is the vault root, identified by `00-INBOX`, `01-CAPTURES`, and `03-BRIEFS`. Ask for the vault path if it is not clear.
2. Read every `00-INBOX` note added in the last 24 hours, `01-CAPTURES` notes added in the last 7 days, `02-CONNECTIONS` notes added in the last 7 days, and recent relevant `1on1s` transcripts. Use available calendar-derived context to prioritize the brief or surface commitments, but persist only source-backed durable insights.
3. Create exactly three sections:
   - **CONNECTIONS:** Three non-obvious connections between recent captures and older notes. Quote relevant passages and link their source files.
   - **PATTERN:** One pattern across the week's material, including what the user's thinking appears to be working toward.
   - **QUESTION:** One non-task question worth sitting with today.
4. Save the result as `03-BRIEFS/brief-YYYY-MM-DD.md`.
5. Print the saved brief in the response.

Do not fabricate note contents or citations. Prefer a smaller, specific result to generic observations.
