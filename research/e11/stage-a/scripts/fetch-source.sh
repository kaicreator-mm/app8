#!/usr/bin/env bash
# SE11 Stage A — fetch exact pinned upstream source commit (shallow, no substitution).
# usage: fetch-source.sh <asset> <github-org/repo> <pinned-sha> [evidence-root]
set -euo pipefail
asset="$1"; repo="$2"; sha="$3"; root="${4:-$(cd "$(dirname "$0")" && pwd)}"

dir="$root/$asset/src"
mkdir -p "$dir"
cd "$dir"
if [ ! -d .git ]; then
  git init -q .
  git remote add origin "https://github.com/$repo.git"
fi
# Frozen-identity checkout: byte-faithful to git blobs (LF), never CRLF-smudged.
git config core.autocrlf false
git config core.eol lf
export HTTPS_PROXY="${HTTPS_PROXY:-http://127.0.0.1:10808}"
export GIT_PROXY_COMMAND=""
git fetch --depth 1 --quiet origin "$sha"
git checkout --quiet --detach FETCH_HEAD

actual_head="$(git rev-parse HEAD)"
actual_tree="$(git rev-parse HEAD^{tree})"
echo "asset=$asset" > "$root/$asset/source-identity.env"
echo "repo=$repo" >> "$root/$asset/source-identity.env"
echo "pinned_sha=$sha" >> "$root/$asset/source-identity.env"
echo "head=$actual_head" >> "$root/$asset/source-identity.env"
echo "tree=$actual_tree" >> "$root/$asset/source-identity.env"
echo "subject=$(git log -1 --format=%s)" >> "$root/$asset/source-identity.env"
echo "commit_date=$(git log -1 --format=%cI)" >> "$root/$asset/source-identity.env"
if [ "$actual_head" != "$sha" ]; then
  echo "FATAL: HEAD $actual_head != pinned $sha (NO_SOURCE_REVISION_SUBSTITUTION violated)" >&2
  exit 2
fi
# Byte-faithful check: with autocrlf=false, any worktree-vs-blob difference
# (including smudge artifacts) shows up as a dirty entry.
dirty=$(git status --porcelain | wc -l)
if [ "$dirty" -ne 0 ]; then
  echo "FATAL: working tree not byte-faithful to HEAD ($dirty dirty entries); run: git -C . checkout -f HEAD" >&2
  exit 3
fi
echo "OK $asset head=$actual_head tree=$actual_tree"
