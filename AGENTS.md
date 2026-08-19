# Shared skills repository

This public repository is the source of truth for reusable skills shared across
Lucas Shin's local coding agents and Hermes Cloud.

## Working rules

- Keep each skill under `skills/<name>/` with `SKILL.md` as its entry point.
- Preserve supporting references, scripts, templates, assets, and provenance with the skill that uses them.
- Never commit credentials, tokens, private keys, environment files, session data, customer material, private project paths, personal-vault contents, or machine-specific caches. This repository is public and is never a secret store.
- Do not replace an existing skill or change its behavior without reviewing the full current definition and relevant supporting files.
- Keep instructions portable across Codex, Claude Code, and Hermes unless a skill explicitly targets one interface.
- Inspect the diff and run the narrowest relevant validation before committing. Validate changed skills with Codex's skill validator when available, and run `shellcheck` plus `sh -n` for shell scripts.
- Run `./scripts/validate-all.sh` before publishing changes.
- Do not force-push or automatically resolve Git conflicts.

Local agents read `skills/` directly. Hermes Cloud consumes the repository as
the public `onchainlu/onchainlu-skills` tap; see `README.md` for setup.
