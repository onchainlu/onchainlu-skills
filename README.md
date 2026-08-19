# onchainlu-skills

Public source of truth for Lucas Shin's reusable agent skills.

The repository is public so local agents and hosted Hermes environments can
install the same skill definitions without repository credentials. Repository
writes remain owner-controlled through GitHub permissions.

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
git clone https://github.com/onchainlu/onchainlu-skills.git ~/.agents
~/.agents/scripts/bootstrap-local.sh
```

The bootstrap script creates missing Claude Code links and configures Hermes when those tools are installed. It does not replace an existing non-symlinked skill.

## Hermes Cloud

Hermes can install this public repository as a skill tap without a GitHub
token. Do not add a token only to read these skills. If a hosted environment
also needs to write to GitHub for another task, keep that credential in the
platform's secret store and outside agent prompts.

From a checkout of this repository inside the Cloud environment, run:

```bash
./scripts/bootstrap-hermes-cloud.sh
```

The script registers `onchainlu/onchainlu-skills` as a public tap and installs
every skill. Hermes runs its normal third-party skill security scan during
installation; the script does not bypass blocked findings.

To install only one skill:

```bash
hermes skills tap add onchainlu/onchainlu-skills
hermes skills install onchainlu/onchainlu-skills/smells --yes
```

## Updating skills

Edit the canonical files under `~/.agents/skills`, review the diff, validate the affected command, then commit and push from `~/.agents`.

Run the complete repository check before publishing:

```bash
./scripts/validate-all.sh
```

The check validates skill frontmatter, OpenAI metadata, local references,
shell scripts, trigger ownership, secret patterns, and public-repository path
boundaries. GitHub Actions runs the same command on pushes and pull requests.

## License and provenance

Original work in this repository is available under the [MIT License](LICENSE).
Some skills were adapted from other repositories or retain separate terms. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for sources, pinned revisions,
and applicable notices.
