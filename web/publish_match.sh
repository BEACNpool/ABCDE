#!/usr/bin/env bash
# publish_match.sh — refresh the BEACN vs grokbot scoreboard and publish it.
#
# Built to be run from cron. It regenerates web/dist/data/match.json from chain
# and pushes it, plus match.html, to gh-pages.
#
# It touches ONLY the three paths the scoreboard owns and pushes as a normal
# fast-forward, so oligarCH/, byttg/, tipsy/, peers/ and the explorer are
# untouched by construction. The orphan-tree force-push in web/deploy_gh_pages.sh
# would delete all of them; that script is self-guarded and must stay that way.
#
# WHY IT PUBLISHES WHEN IT DOES: gh-pages is a branch of a repo whose whole
# pitch is "one clone away". Cron polls every 5 min so a swap shows up on the
# page in one block-plus-poll. It publishes when the CHAIN changed -- a balance
# moved, a transaction landed -- when the lead chart gained a point, or when the
# published snapshot is older than MATCH_MAX_AGE (default 15 min), so the USD
# mark and the page timestamp stay honest while people are watching.
# match.json is ~16 KB and the history ~50 bytes per point; git stores deltas.
#
# THE PUBLISHED HISTORY IS THE SOURCE OF TRUTH, not a local file. The worktree
# is synced to origin/gh-pages FIRST, the published history is copied back into
# dist, and the new point is appended to that. So the lead chart survives losing
# this box entirely, and it is identical no matter which machine runs the job.
# ⚠️ A point that is not published is LOST: the next run re-adopts the published
# history and overwrites the local copy. That is deliberate (one source of
# truth), but it means "record a point" and "publish" cannot be decoupled.
#
#   ./web/publish_match.sh              refresh, publish if warranted
#   ./web/publish_match.sh --force      publish regardless
#   ./web/publish_match.sh --dry-run    refresh and report, push nothing
#
# Kill switch: set MATCH_PUBLISH_DISABLED=1 (in the environment or the crontab
# line) and it exits without touching anything.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$REPO/web/dist"
JSON="$DIST/data/match.json"
HIST="$DIST/data/match_history.json"
# Deliberately NOT the worktree web/publish_gh_pages.sh uses: that one does a
# hard reset, and a cron colliding with a manual publish would discard work.
# It is also DETACHED. Git lets only one worktree hold a branch, so an attached
# copy here makes `publish_gh_pages.sh` fail with "gh-pages is already used by
# worktree" -- a scheduled job must never be able to block the manual publisher.
WORKTREE="${MATCH_WORKTREE:-$REPO/.worktrees/gh-pages-match}"
MAX_AGE="${MATCH_MAX_AGE:-900}"
LOCK="${MATCH_LOCK:-$REPO/.worktrees/publish_match.lock}"
PY="$REPO/.venv/bin/python3"; [[ -x "$PY" ]] || PY=python3

# Cron is 5 min. A hung Koios call must not start a second git worktree reset.
mkdir -p "$(dirname "$LOCK")"
exec 9>"$LOCK"
if ! /usr/bin/flock -n 9; then
  echo "$(date -u +%FT%TZ) publish_match: previous run still holds the lock, skipping"
  exit 0
fi

FORCE=0; DRY=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --dry-run) DRY=1 ;;
    *) echo "unknown argument: $arg" >&2; exit 64 ;;
  esac
done

if [[ "${MATCH_PUBLISH_DISABLED:-0}" == "1" ]]; then
  echo "$(date -u +%FT%TZ) publish_match: DISABLED by MATCH_PUBLISH_DISABLED"
  exit 0
fi

echo "$(date -u +%FT%TZ) 1/4 syncing the worktree to origin/gh-pages"
git -C "$REPO" fetch origin gh-pages --quiet
if [[ ! -d "$WORKTREE" ]]; then
  git -C "$REPO" worktree add --detach "$WORKTREE" origin/gh-pages --quiet
fi
git -C "$WORKTREE" reset --hard origin/gh-pages --quiet

# Adopt the PUBLISHED history before appending, so the chart is rebuilt from
# what the world can see rather than from whatever this box happens to hold.
mkdir -p "$DIST/data"
if [[ -f "$WORKTREE/data/match_history.json" ]]; then
  cp "$WORKTREE/data/match_history.json" "$HIST"
fi

echo "2/4 refreshing the snapshot from chain"
"$PY" "$REPO/scripts/match_snapshot.py" --out "$JSON" --history "$HIST" \
      ${MATCH_BACKFILL:+--backfill} --quiet

echo "3/4 syntax-checking the page"
"$PY" "$REPO/scripts/verify_web_pages.py" >/dev/null

PUBLISHED="$WORKTREE/data/match.json"
REASON="$("$PY" - "$JSON" "$PUBLISHED" "$MAX_AGE" "$HIST" "$WORKTREE/data/match_history.json" <<'PYEOF'
import json, sys, time
new_path, old_path, max_age, hist_new, hist_old = (
    sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5])
new = json.load(open(new_path))
try:
    old = json.load(open(old_path))
except Exception:
    print("nothing published yet"); raise SystemExit
if old.get("chain_fingerprint") != new.get("chain_fingerprint"):
    print("the chain moved"); raise SystemExit


def n_points(path):
    try:
        return len(json.load(open(path)).get("points", []))
    except Exception:
        return 0


gained = n_points(hist_new) - n_points(hist_old)
if gained > 0:
    print(f"{gained} new point(s) on the lead chart"); raise SystemExit
age = time.time() - old.get("generated_at_unix", 0)
if age > max_age:
    print(f"published snapshot is {int(age)}s old"); raise SystemExit
print("")
PYEOF
)"

if [[ -z "$REASON" && "$FORCE" -eq 0 ]]; then
  echo "4/4 nothing worth publishing — chain unchanged and the live snapshot is fresh"
  exit 0
fi
[[ "$FORCE" -eq 1 && -z "$REASON" ]] && REASON="--force"

if [[ "$DRY" -eq 1 ]]; then
  echo "4/4 DRY RUN — would publish ($REASON)"
  exit 0
fi

echo "4/4 publishing ($REASON)"
mkdir -p "$WORKTREE/data"
cp "$DIST/match.html" "$WORKTREE/match.html"
cp "$JSON" "$WORKTREE/data/match.json"
cp "$HIST" "$WORKTREE/data/match_history.json"

cd "$WORKTREE"
git add -A match.html data/match.json data/match_history.json
if git diff --cached --quiet; then
  echo "  nothing changed on disk"
  exit 0
fi
git -c user.name='BEACN deploy' -c user.email='deploy@beacnpool' \
    commit -qm "Match scoreboard $(date -u +%FT%TZ) ($REASON)"
git fetch origin gh-pages --quiet
# The hourly peer-map cron and the explorer publisher push here too. Rebase,
# never force. Pushing HEAD explicitly because this worktree is detached.
git merge-base --is-ancestor origin/gh-pages HEAD || git rebase origin/gh-pages --quiet
git push origin HEAD:gh-pages --quiet
echo "done -> https://beacnpool.github.io/ABCDE/match.html"
