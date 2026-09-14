---
name: gif-search
description: "Search/download GIFs from Tenor via curl + jq."
license: MIT
metadata:
  hermes:
    tags: [GIF, Search, Download, Tenor, API]
---

# GIF Search (Tenor API)

Search and download GIFs through the Tenor API with `curl` and `jq`. This skill is fail-closed: do not make a request unless `TENOR_API_KEY` is set and both required commands are available.

## When to use

Useful for finding reaction GIFs, creating visual content, and sending GIFs in chat.

## Setup

Store the Tenor API key in the existing Hermes environment file; do not put it in a command-line URL or any process-visible argument, and never print its value:

```bash
source "${HERMES_HOME:-$HOME/.hermes}/.env"
```

The `.env` file should contain the secret assignment (with an actual key value, kept private):

```dotenv
TENOR_API_KEY=your_key_here
```

Get a free API key at https://developers.google.com/tenor/guides/quickstart. Do not paste the key into chat, scripts, URLs, shell history, logs, or command output.

## Prerequisites

- `curl` must be installed and available on `PATH`.
- `jq` must be installed and available on `PATH`.
- `TENOR_API_KEY` must be non-empty after sourcing the existing `.env` file.

Check command availability without exposing the key:

```bash
command -v curl >/dev/null && command -v jq >/dev/null
[ -n "${TENOR_API_KEY:-}" ]
```

If any prerequisite is missing, stop without making a request or attempting a partial search.

## Search for GIFs

Use curl's config input so the key is not part of a URL or process-visible argument. `--data-urlencode` encodes spaces and special characters in every parameter. The unquoted heredoc expands the environment variable into curl's stdin; it does not print the value.

```bash
# Search and get GIF URLs; no key value appears in the URL or argv
curl --silent --show-error --fail --get --config - <<EOF | jq -r '.results[]?.media_formats.gif?.url // empty'
url = "https://tenor.googleapis.com/v2/search"
data-urlencode = "q=thumbs up & 50%"
data-urlencode = "limit=5"
data-urlencode = "key=$TENOR_API_KEY"
EOF
```

For smaller previews, guard the optional format so results without it are skipped:

```bash
curl --silent --show-error --fail --get --config - <<EOF | jq -r '.results[]?.media_formats.tinygif?.url // empty'
url = "https://tenor.googleapis.com/v2/search"
data-urlencode = "q=nice work"
data-urlencode = "limit=3"
data-urlencode = "key=$TENOR_API_KEY"
EOF
```

Never replace the config-input pattern with a URL containing `key=...` or with a command-line argument containing the key. Do not use `set -x` while handling the environment file or request.

## Download a GIF safely

Select a URL only when the requested format exists, and refuse to overwrite an existing destination:

```bash
URL=$(curl --silent --show-error --fail --get --config - <<EOF | jq -r '.results[0]?.media_formats.gif?.url // empty'
url = "https://tenor.googleapis.com/v2/search"
data-urlencode = "q=celebration"
data-urlencode = "limit=1"
data-urlencode = "key=$TENOR_API_KEY"
EOF
)
[ -n "$URL" ] || { printf '%s\n' 'No GIF URL found' >&2; exit 1; }
[ ! -e celebration.gif ] || { printf '%s\n' 'Refusing to overwrite celebration.gif' >&2; exit 1; }
curl --silent --show-error --fail --location --output celebration.gif "$URL"
```

The API key is supplied only through curl's stdin configuration. The returned media URL is safe to pass as the download argument, but treat it as untrusted input and do not overwrite files. If the requested media format is absent, stop rather than passing `null` or an empty URL to curl.

## Get Full Metadata

```bash
curl --silent --show-error --fail --get --config - <<EOF | jq '.results[]? | {title: (.title // ""), url: (.media_formats.gif?.url // null), preview: (.media_formats.tinygif?.url // null), dimensions: (.media_formats.gif?.dims // null)}'
url = "https://tenor.googleapis.com/v2/search"
data-urlencode = "q=cat"
data-urlencode = "limit=3"
data-urlencode = "key=$TENOR_API_KEY"
EOF
```

Missing formats are represented as `null` in metadata; do not dereference them as if every result contains every format.

## API Parameters

| Parameter | Description |
|-----------|-------------|
| `q` | Search query; pass through `curl`'s `--data-urlencode` config option |
| `limit` | Max results (1–50, default 20) |
| `key` | API key supplied from `$TENOR_API_KEY` through curl config stdin; never place the value in a URL or argv |
| `media_filter` | Filter formats: `gif`, `tinygif`, `mp4`, `tinymp4`, `webm` |
| `contentfilter` | Safety: `off`, `low`, `medium`, `high` |
| `locale` | Language: `en_US`, `es`, `fr`, etc. |

## Available Media Formats

Each result may have formats under `.media_formats`; a format can be absent and must be checked before use:

| Format | Use case |
|--------|----------|
| `gif` | Full quality GIF |
| `tinygif` | Small preview GIF |
| `mp4` | Video version (smaller file size) |
| `tinymp4` | Small preview video |
| `webm` | WebM video |
| `nanogif` | Tiny thumbnail |

## Notes

- URL-encode every query parameter with `--data-urlencode`; do not hand-build URLs with unescaped spaces or special characters.
- For sending in chat, `tinygif` URLs are lighter weight when that format is present.
- GIF URLs can be used directly in markdown only after checking that a non-empty URL was returned.
- Keep `TENOR_API_KEY` in the existing environment file and out of command-line URLs, process arguments, logs, and output.
