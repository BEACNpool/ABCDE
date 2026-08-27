#!/usr/bin/env bash
# ⛔ DO NOT RUN THIS. Use web/publish_gh_pages.sh instead.
#
# This script force-pushes an ORPHAN tree built from web/dist alone. gh-pages
# also carries oligarCH/, oligarch/, byttg/ and tipsy/ (public, minted NFT pages)
# and peers/ (rebuilt hourly). Running this deletes all of them and the branch's
# entire history. It is kept only for reference.
set -euo pipefail
echo "REFUSING: this would force-push an orphan tree and delete oligarCH/, byttg/," >&2
echo "tipsy/ and peers/ from gh-pages. Use web/publish_gh_pages.sh." >&2
exit 1

# ---- original script below, unreachable ----
# Deploy the ABCDE explorer to the gh-pages branch (served by GitHub Pages).
#
# The site is fully static and client-side (DuckDB-WASM + prebuilt JSON), so
# "deploy" = rebuild the data layer from the committed DuckDB, then force-push a
# single-commit orphan tree to gh-pages. This never touches main's history.
#
# GitHub Pages must be enabled once (Settings -> Pages -> Deploy from a branch
# -> gh-pages -> / root). Live URL: https://beacnpool.github.io/ABCDE/
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$REPO/.venv/bin/python3"; [[ -x "$PY" ]] || PY=python3
REMOTE="git@github-abcde:BEACNpool/ABCDE.git"
DIST="$REPO/web/dist"
STAGE="$(mktemp -d)"

echo "1/3 rebuild data layer + OG share cards"
"$PY" "$REPO/web/build_web_data.py" >/dev/null
# OG cards use Pillow, which is on the system python (not the venv). Best-effort.
python3 "$REPO/scripts/build_og_cards.py" || echo "  (og cards skipped: $?)"

echo "2/3 stage site"
cp -r "$DIST/." "$STAGE/"
rm -f "$STAGE"/_smoke_*.png
touch "$STAGE/.nojekyll"   # serve data/ subdirs verbatim, no Jekyll
printf 'abcde-explorer\n' > "$STAGE/README.md"

echo "3/3 force-push gh-pages"
( cd "$STAGE"
  git init -q
  git checkout -q -b gh-pages
  git add -A
  git -c user.name='BEACN deploy' -c user.email='deploy@beacnpool' \
      commit -qm "Deploy ABCDE explorer $(date -u +%FT%TZ)"
  git push -qf "$REMOTE" gh-pages )
rm -rf "$STAGE"
echo "done -> https://beacnpool.github.io/ABCDE/  (enable Pages: Settings -> Pages -> gh-pages / root)"
