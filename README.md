# onchainlu-skills

Private source of truth for Lucas Shin's reusable agent skills.

## Repository layout

Each command lives at `skills/<name>/SKILL.md`. Supporting files stay inside the same skill directory.

The repository is designed to be checked out at `~/.agents`:

```text
~/.agents/
├── README.md
├── scripts/
└── skills/
    ├── audit-only/
    │   └── SKILL.md
    ├── smells/
    │   └── SKILL.md
    └── ...
```

## Local agents

Codex discovers skills in `~/.agents/skills` directly. Claude Code uses per-skill links under `~/.claude/skills`. Hermes reads the same source through `skills.external_dirs` in its `config.yaml`.

On a new machine:

```bash
gh repo clone onchainlu/onchainlu-skills ~/.agents
~/.agents/scripts/bootstrap-local.sh
```

The bootstrap script creates missing Claude Code links and configures Hermes when those tools are installed. It does not replace an existing non-symlinked skill.

## Hermes Cloud

Hermes supports private GitHub repositories as skill taps. The Cloud environment must have read access to `onchainlu/onchainlu-skills` through its GitHub App, an authenticated `gh` CLI, or `GITHUB_TOKEN`/`GH_TOKEN`. If a token is required, use a fine-grained token with read-only Contents access and keep it in the platform's secret store. Never commit it or paste it into a prompt.

From a checkout of this repository inside the Cloud environment, run:

```bash
./scripts/bootstrap-hermes-cloud.sh
```

The script registers `onchainlu/onchainlu-skills` as a private tap and installs every skill. Hermes runs its normal third-party skill security scan during installation; the script does not bypass blocked findings.

To install only one skill:

```bash
hermes skills tap add onchainlu/onchainlu-skills
hermes skills install onchainlu/onchainlu-skills/smells --yes
```

## Updating skills

Edit the canonical files under `~/.agents/skills`, review the diff, validate the affected command, then commit and push from `~/.agents`.
