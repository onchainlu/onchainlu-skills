---
name: github-issues
description: "Create, triage, label, assign GitHub issues via gh or REST."
license: MIT
metadata:
  hermes:
    tags: [GitHub, Issues, Project-Management, Bug-Tracking, Triage]
    related_skills: [github-auth, github-pr-workflow]
---

# GitHub Issues Management

Create, search, triage, and manage GitHub issues. Each section shows `gh` first, then the `curl` fallback.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)
- Inside a git repo with a GitHub remote, or specify the repo explicitly

### Setup

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="curl"
  # Curl fallback accepts only a token already exported by the user.
  # Never read credential files, print the token, or persist it in a receipt.
  if [ -z "${GITHUB_TOKEN:-}" ]; then
    printf '%s\n' 'GITHUB_TOKEN must already be exported for the curl fallback.' >&2
    exit 1
  fi
fi

REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

### Bounded curl/HTTP fallback contract

Use `gh` for authenticated operations when available. If using curl, every request must use
`--fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576`,
`Accept: application/vnd.github+json`, and `Content-Type: application/json` for requests with a body.
Treat non-2xx status, non-JSON content, invalid JSON, an error object, or an unexpected top-level
schema as failure and stop; do not continue with partial data. Validate the response before rendering
it, cap candidate/result counts, and emit only a redacted receipt containing operation, endpoint
(without credentials), status, bounded counts, and verified item numbers. Never print raw responses,
headers, request bodies, authorization values, or issue bodies containing secrets.


---

## 1. Viewing Issues

**With gh:**

```bash
gh issue list
gh issue list --state open --label "bug"
gh issue list --assignee @me
gh issue list --search "authentication error" --state all
gh issue view 42
```

**With curl:**

```bash
# List open issues
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&per_page=20" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:  # GitHub API returns PRs in /issues too
        labels = ', '.join(l['name'] for l in i['labels'])
        print(f\"#{i['number']:5}  {i['state']:6}  {labels:30}  {i['title']}\")"

# Filter by label
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?state=open&labels=bug&per_page=20" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:
        print(f\"#{i['number']}  {i['title']}\")"

# View a specific issue
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  | python3 -c "
import sys, json
i = json.load(sys.stdin)
labels = ', '.join(l['name'] for l in i['labels'])
assignees = ', '.join(a['login'] for a in i['assignees'])
print(f\"#{i['number']}: {i['title']}\")
print(f\"State: {i['state']}  Labels: {labels}  Assignees: {assignees}\")
print(f\"Author: {i['user']['login']}  Created: {i['created_at']}\")
print(f\"\n{i['body']}\")"

# Search issues
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  "https://api.github.com/search/issues?q=authentication+error+repo:$OWNER/$REPO" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin)['items']:
    print(f\"#{i['number']}  {i['state']:6}  {i['title']}\")"
```

## 2. Creating Issues

**With gh:**

```bash
gh issue create \
  --title "Login redirect ignores ?next= parameter" \
  --body "## Description
After logging in, users always land on /dashboard.

## Steps to Reproduce
1. Navigate to /settings while logged out
2. Get redirected to /login?next=/settings
3. Log in
4. Actual: redirected to /dashboard (should go to /settings)

## Expected Behavior
Respect the ?next= query parameter." \
  --label "bug,backend" \
  --assignee "username"
```

**With curl:**

```bash
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/$OWNER/$REPO/issues \
  -d '{
    "title": "Login redirect ignores ?next= parameter",
    "body": "## Description\nAfter logging in, users always land on /dashboard.\n\n## Steps to Reproduce\n1. Navigate to /settings while logged out\n2. Get redirected to /login?next=/settings\n3. Log in\n4. Actual: redirected to /dashboard\n\n## Expected Behavior\nRespect the ?next= query parameter.",
    "labels": ["bug", "backend"],
    "assignees": ["username"]
  }'
```

### Bug Report Template

```
## Bug Description
<What's happening>

## Steps to Reproduce
1. <step>
2. <step>

## Expected Behavior
<What should happen>

## Actual Behavior
<What actually happens>

## Environment
- OS: <os>
- Version: <version>
```

### Feature Request Template

```
## Feature Description
<What you want>

## Motivation
<Why this would be useful>

## Proposed Solution
<How it could work>

## Alternatives Considered
<Other approaches>
```

## 3. Managing Issues

### Add/Remove Labels

**With gh:**

```bash
gh issue edit 42 --add-label "priority:high,bug"
gh issue edit 42 --remove-label "needs-triage"
```

**With curl:**

```bash
# Add labels
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/labels \
  -d '{"labels": ["priority:high", "bug"]}'

# Remove a label
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 -X DELETE \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/labels/needs-triage

# List available labels in the repo
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/$OWNER/$REPO/labels \
  | python3 -c "
import sys, json
for l in json.load(sys.stdin):
    print(f\"  {l['name']:30}  {l.get('description', '')}\")"
```

### Assignment

**With gh:**

```bash
gh issue edit 42 --add-assignee username
gh issue edit 42 --add-assignee @me
```

**With curl:**

```bash
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/assignees \
  -d '{"assignees": ["username"]}'
```

### Commenting

**With gh:**

```bash
gh issue comment 42 --body "Investigated — root cause is in auth middleware. Working on a fix."
```

**With curl:**

```bash
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42/comments \
  -d '{"body": "Investigated — root cause is in auth middleware. Working on a fix."}'
```

### Closing and Reopening

**With gh:**

```bash
gh issue close 42
gh issue close 42 --reason "not planned"
gh issue reopen 42
```

**With curl:**

```bash
# Close
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  -d '{"state": "closed", "state_reason": "completed"}'

# Reopen
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/$OWNER/$REPO/issues/42 \
  -d '{"state": "open"}'
```

### Linking Issues to PRs

GitHub can close a linked issue when a PR containing a supported closing keyword
merges successfully into the repository's configured default branch; this behavior is subject to
repository settings, permissions, and the issue/PR relationship. Verify the issue state after merge;
do not treat the keyword alone as proof of closure.

```
Closes #42
Fixes #42
Resolves #42
```

To create a branch from an issue:

**With gh:**

```bash
gh issue develop 42 --checkout
```

**With git (manual equivalent):**

```bash
git checkout main && git pull origin main
git checkout -b fix/issue-42-login-redirect
```

## 4. Issue Triage Workflow

When asked to triage issues:

1. **List untriaged issues:**

```bash
# With gh
gh issue list --label "needs-triage" --state open

# With curl
curl --fail-with-body --silent --show-error --connect-timeout 5 --max-time 20 --max-filesize 1048576 \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$OWNER/$REPO/issues?labels=needs-triage&state=open" \
  | python3 -c "
import sys, json
for i in json.load(sys.stdin):
    if 'pull_request' not in i:
        print(f\"#{i['number']}  {i['title']}\")"
```

2. **Read and categorize** each issue (view details, understand the bug/feature)

3. **Apply labels and priority** (see Managing Issues above)

4. **Assign** if the owner is clear

5. **Comment with triage notes** if needed

## 5. Bulk Operations

Bulk close is a destructive operation. Use a preview-first, bounded workflow; never document it as
an unbounded `xargs` or shell-pipeline one-liner.

**With gh (preferred):**

```bash
MAX_ITEMS=50
mapfile -t candidates < <(
  gh issue list --label "wontfix" --state open --limit "$((MAX_ITEMS + 1))" \
    --json number,pullRequest --jq '[.[] | select(.pullRequest == null) | .number] | .[]'
)
if [ "${#candidates[@]}" -gt "$MAX_ITEMS" ]; then
  printf '%s\n' 'Refusing bulk close: candidate count exceeds the hard limit.' >&2
  exit 1
fi
printf 'Preview (issues only, max %s): %s\n' "$MAX_ITEMS" "${candidates[*]:-none}"
read -r -p 'Type CLOSE to confirm this exact preview: ' confirmation
[ "$confirmation" = CLOSE ] || { printf '%s\n' 'Cancelled.' >&2; exit 1; }
for num in "${candidates[@]}"; do
  gh issue close "$num" --reason "not planned" || { printf 'Failed at #%s; stopping.\n' "$num" >&2; exit 1; }
  state=$(gh issue view "$num" --json state --jq .state) || { printf 'Could not verify #%s; stopping.\n' "$num" >&2; exit 1; }
  [ "$state" = closed ] || { printf 'Verification failed for #%s; stopping.\n' "$num" >&2; exit 1; }
  printf 'verified closed #%s\n' "$num"
done
```

**With curl:** use the same immutable preview, `MAX_ITEMS` limit, explicit `CLOSE` confirmation,
PR exclusion, per-item stop-on-error behavior, and post-mutation state verification. Each request
must follow the bounded curl/HTTP contract above and produce only a redacted receipt; abort on any
HTTP, content-type, schema, JSON, or verification failure. Do not use `xargs`, unbounded loops, or
print `Closed` unless the subsequent state query verified the item is closed.

## Quick Reference Table

| Action | gh | curl endpoint |
|--------|-----|--------------|
| List issues | `gh issue list` | `GET /repos/{o}/{r}/issues` |
| View issue | `gh issue view N` | `GET /repos/{o}/{r}/issues/N` |
| Create issue | `gh issue create ...` | `POST /repos/{o}/{r}/issues` |
| Add labels | `gh issue edit N --add-label ...` | `POST /repos/{o}/{r}/issues/N/labels` |
| Assign | `gh issue edit N --add-assignee ...` | `POST /repos/{o}/{r}/issues/N/assignees` |
| Comment | `gh issue comment N --body ...` | `POST /repos/{o}/{r}/issues/N/comments` |
| Close | `gh issue close N` | `PATCH /repos/{o}/{r}/issues/N` |
| Search | `gh issue list --search "..."` | `GET /search/issues?q=...` |
