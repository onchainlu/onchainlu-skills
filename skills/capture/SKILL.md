---
name: capture
description: Capture supplied text as a new note in an Obsidian vault inbox. Use when the user wants to save a thought, observation, quote, or raw note to 00-INBOX.
---

# Capture to Vault

1. Confirm the vault root contains `00-INBOX`. If it is missing, stop and ask for the vault path or confirmation to create the inbox; do not capture anything yet.
2. Use the supplied text as the complete note body. If no text is supplied, ask for it.
3. Create `00-INBOX/YYYY-MM-DD-<slug>.md`, where `<slug>` comes from the first 60 characters and is safe for a filename.
4. Add this frontmatter:

```yaml
---
created: YYYY-MM-DD
tags: []
type: capture
source: codex
---
```

5. Confirm the created relative path. Do not edit or classify the note during capture.
