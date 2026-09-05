#!/usr/bin/env bash
# publish_match.sh — refresh the BEACN vs grokbot scoreboard and publish it.
#
# Built to be run from cron. It regenerates web/dist/data/match.json from chain
# and pushes it, plus the match page and its social preview assets, to gh-pages.
#
# It touches ONLY the scoreboard paths (match.html, the social preview,
# match.json, match_history.json, match-venues/) and pushes as a normal
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
# The lock is for overlapping RUNS, not a parking brake. Disable with
# MATCH_PUBLISH_DISABLED=1. A dummy `flock … read _` held this overnight on
# 2026-08-30 and the public page went stale for 8 hours.
LOCK_STALE_SEC="${MATCH_LOCK_STALE_SEC:-600}"
PUBLISH_TIMEOUT="${MATCH_PUBLISH_TIMEOUT:-240}"

lock_holders() {
  local p
  for p in $(/usr/bin/fuser "$LOCK" 2>/dev/null); do
    [[ "$p" == "$$" ]] && continue
    printf '%s\n' "$p"
  done
}

holder_cmd() {
  local f="/proc/$1/cmdline"
  [[ -r "$f" ]] || { printf ''; return 0; }
  tr '\0' ' ' < "$f" 2>/dev/null || true
}

holder_age() {
  local n
  n=$(ps -o etimes= -p "$1" 2>/dev/null | tr -d ' ')
  printf '%s' "${n:-0}"
}

# A live publish is this script, still younger than LOCK_STALE_SEC.
# Anything else holding the file (a parked `flock … read _`, a leftover
# watchdog sleep that inherited fd 9) is stale and gets stolen.
holder_is_live_publish() {
  local cmd age
  cmd=$(holder_cmd "$1")
  age=$(holder_age "$1")
  [[ "$cmd" == *publish_match.sh* && "$age" -lt "$LOCK_STALE_SEC" ]]
}

mkdir -p "$(dirname "$LOCK")"
exec 9>"$LOCK"
if ! /usr/bin/flock -n 9; then
  stale=()
  live=0
  while read -r p; do
    [[ -z "$p" ]] && continue
    echo "$(date -u +%FT%TZ) publish_match: lock held by pid $p age=$(holder_age "$p")s cmd=$(holder_cmd "$p")"
    if holder_is_live_publish "$p"; then
      live=1
    else
      stale+=("$p")
    fi
  done < <(lock_holders)
  if [[ "$live" -eq 1 ]]; then
    echo "$(date -u +%FT%TZ) publish_match: previous run still holds the lock, skipping"
    exit 0
  fi
  if [[ ${#stale[@]} -eq 0 ]]; then
    echo "$(date -u +%FT%TZ) publish_match: previous run still holds the lock, skipping"
    exit 0
  fi
  echo "$(date -u +%FT%TZ) publish_match: stealing stale lock from ${stale[*]}"
  kill -TERM "${stale[@]}" 2>/dev/null || true
  sleep 1
  kill -KILL "${stale[@]}" 2>/dev/null || true
  if ! /usr/bin/flock -n 9; then
    echo "$(date -u +%FT%TZ) publish_match: lock still held after steal, skipping"
    exit 0
  fi
fi

# A publish that has not finished in PUBLISH_TIMEOUT seconds is stuck. TERM
# this process so the flock fd closes and the next cron can run. The kill
# switch remains MATCH_PUBLISH_DISABLED=1, not parking the lock.
# setsid: a background sleep in this process group would hold cron/ssh open
# until the timer fired (measured 2026-08-30: a finished publish sat 4 min).
watchdog_pid=""
if [[ -z "${MATCH_PUBLISH_WATCHED:-}" ]]; then
  parent=$$
  # Close inherited lock fd 9. A watchdog that keeps it open holds the
  # flock after this script exits, and cron then skips until the timer dies.
  watchdog_pid=$(setsid /bin/sh -c '
    exec 9<&- 9>&-
    sleep "$1"
    kill -TERM '"$parent"' 2>/dev/null || true
  ' sh "$PUBLISH_TIMEOUT" </dev/null >/dev/null 2>&1 & echo $!)
  trap 'if [[ -n "$watchdog_pid" ]]; then kill -TERM -"$watchdog_pid" 2>/dev/null || kill -TERM "$watchdog_pid" 2>/dev/null || true; fi' EXIT
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

echo "3/4 verifying the snapshot and page"
"$PY" "$REPO/scripts/verify_match_snapshot.py" "$JSON" >/dev/null
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
mkdir -p "$WORKTREE/data" "$WORKTREE/match-venues" "$WORKTREE/match-share" "$WORKTREE/brand"
cp -a "$DIST/brand/." "$WORKTREE/brand/"
cp -a "$DIST/match-share/." "$WORKTREE/match-share/"
cp "$DIST/match.html" "$WORKTREE/match.html"
cp "$DIST/match-social.svg" "$WORKTREE/match-social.svg"
cp "$DIST/match-social.png" "$WORKTREE/match-social.png"
cp "$JSON" "$WORKTREE/data/match.json"
cp "$HIST" "$WORKTREE/data/match_history.json"
if [[ -d "$DIST/match-venues" ]]; then
  cp -a "$DIST/match-venues/." "$WORKTREE/match-venues/"
fi

cd "$WORKTREE"
git add -A match.html match-social.svg match-social.png match-venues match-share brand data/match.json data/match_history.json
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
