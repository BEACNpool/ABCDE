#!/usr/bin/env bash
# publish_gh_pages.sh — publish the explorer to gh-pages WITHOUT destroying it.
#
# gh-pages carries far more than web/dist: oligarCH/, oligarch/, byttg/, tipsy/
# (public, minted NFT pages) and peers/ (rebuilt hourly by ops/peer_map_collect.py
# on the workhorse). The older web/deploy_gh_pages.sh force-pushes an ORPHAN tree
# built from web/dist alone, which deletes every one of those plus the branch's
# history. Use this instead.
#
# It touches only the paths the explorer owns, and pushes as a normal
# fast-forward, so anything else on the branch is untouched by construction.
#
# It also publishes media/, og/ and r/. Those are generated and gitignored in
# main on purpose ("zero clone weight") -- which meant nothing ever deployed
# them, and the README's tour video, the homepage's social image and every share
# permalink 404'd from 2026-07-24 until they were noticed on 2026-08-27.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$REPO/web/dist"
WORKTREE="${GHPAGES_WORKTREE:-$REPO/.worktrees/gh-pages}"
PY="$REPO/.venv/bin/python3"; [[ -x "$PY" ]] || PY=python3

# Only these are ours. Everything else on gh-pages is left alone.
OWNED_FILES=(index.html relays.html app.js style.css)
OWNED_DIRS=(data media og r)

echo "1/5 rebuild the data layer"
"$PY" "$REPO/web/build_web_data.py" >/dev/null
python3 "$REPO/scripts/build_og_cards.py" >/dev/null 2>&1 || echo "  (og cards skipped — Pillow missing)"

echo "2/5 syntax-check the pages"
python3 "$REPO/scripts/verify_web_pages.py"

echo "3/5 sync the worktree to origin/gh-pages"
if [[ ! -d "$WORKTREE" ]]; then
  git -C "$REPO" worktree add "$WORKTREE" gh-pages --quiet
fi
git -C "$WORKTREE" fetch origin gh-pages --quiet
git -C "$WORKTREE" reset --hard origin/gh-pages --quiet

echo "4/5 copy the explorer's own paths"
for f in "${OWNED_FILES[@]}"; do
  [[ -f "$DIST/$f" ]] && cp "$DIST/$f" "$WORKTREE/$f"
done
for d in "${OWNED_DIRS[@]}"; do
  [[ -d "$DIST/$d" ]] || continue
  mkdir -p "$WORKTREE/$d"
  cp -r "$DIST/$d/." "$WORKTREE/$d/"
done
rm -f "$WORKTREE"/og/_smoke_*.png "$WORKTREE"/_smoke_*.png

echo "5/5 commit + fast-forward push"
cd "$WORKTREE"
git add -A
if git diff --cached --quiet; then
  echo "  nothing changed"
  exit 0
fi
git -c user.name='BEACN deploy' -c user.email='deploy@beacnpool' \
    commit -qm "${1:-Publish ABCDE explorer $(date -u +%FT%TZ)}"
git fetch origin gh-pages --quiet
# The hourly peer-map cron pushes to this branch too; rebase rather than force.
git merge-base --is-ancestor origin/gh-pages HEAD || git rebase origin/gh-pages --quiet
git push origin gh-pages
echo "done -> https://beacnpool.github.io/ABCDE/  (Pages takes a minute to rebuild)"
