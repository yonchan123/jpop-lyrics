#!/usr/bin/env bash
# Publish the latest snapshot of this repo.
#
#   changyeon/jpop-lyrics (private) : full tree
#   yonchan123/jpop-lyrics (public)  : full tree minus paths listed in .publish-exclude
#
# Both remotes receive a single orphan commit (no history), force-pushed.
#
# Usage:
#   scripts/publish.sh [--dry-run] [--only changyeon|yonchan] [--no-snapshot]
#
#   --dry-run      build commits and show what would be excluded; push nothing
#   --only X       push to just one remote
#   --no-snapshot  don't squash local main; publish the current HEAD tree as is
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

DRY=0; ONLY=""; SNAPSHOT=1
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --only) ONLY="${2:?--only needs changyeon|yonchan}"; shift ;;
    --no-snapshot) SNAPSHOT=0 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done
case "$ONLY" in ""|changyeon|yonchan) ;; *) echo "--only must be changyeon or yonchan" >&2; exit 2 ;; esac

MSG="Latest snapshot: J-pop/J-rock lyric translations (JA→KO 3-line)"
EXCLUDE_FILE="$ROOT/.publish-exclude"

# ---- 1. Squash working tree into a single orphan commit on local main ----
if [ "$SNAPSHOT" = 1 ] && [ "$DRY" = 0 ]; then
  git add -A
  git checkout --orphan snapshot-latest -q
  git commit -q -m "$MSG"
  git branch -D main -q && git branch -m main
fi
FULL_COMMIT=$(git rev-parse HEAD)

# ---- 2. Build the public tree (excluded paths removed) in a temp index ----
EXCLUDES=()
if [ -f "$EXCLUDE_FILE" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%#*}"                              # strip comments
    line="$(printf '%s' "$line" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')"
    [ -z "$line" ] && continue
    line="${line%/}"
    case "$line" in /*|*..*) echo "refusing unsafe exclude path: $line" >&2; exit 1 ;; esac
    EXCLUDES+=("$line")
  done < "$EXCLUDE_FILE"
fi

TMP_INDEX=$(mktemp)
trap 'rm -f "$TMP_INDEX"' EXIT
GIT_INDEX_FILE="$TMP_INDEX" git read-tree "$FULL_COMMIT^{tree}"

echo "== Excluded from yonchan (public) =="
if [ ${#EXCLUDES[@]} -eq 0 ]; then echo "  (none)"; fi
for p in "${EXCLUDES[@]+"${EXCLUDES[@]}"}"; do
  n=$(GIT_INDEX_FILE="$TMP_INDEX" git ls-files -- "$p" | wc -l | tr -d ' ')
  if [ "$n" = 0 ]; then
    echo "  $p  (not in tree — nothing to exclude)"
  else
    GIT_INDEX_FILE="$TMP_INDEX" git rm -r -q --cached -- "$p"
    echo "  $p  ($n files)"
  fi
done
PUBLIC_TREE=$(GIT_INDEX_FILE="$TMP_INDEX" git write-tree)

# Safety: nothing excluded may survive in the public tree
for p in "${EXCLUDES[@]+"${EXCLUDES[@]}"}"; do
  if git ls-tree -r --name-only "$PUBLIC_TREE" -- "$p" | grep -q .; then
    echo "ABORT: $p still present in public tree" >&2; exit 1
  fi
done

# Warn about public files that link into excluded paths (broken links on yonchan)
for p in "${EXCLUDES[@]+"${EXCLUDES[@]}"}"; do
  enc=$(python3 -I -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$p")
  hits=$(git grep -l -F -e "]($p" -e "]($enc" "$PUBLIC_TREE" -- '*.md' 2>/dev/null | sed "s/^$PUBLIC_TREE://" || true)
  [ -n "$hits" ] && echo "  WARN: public files link to excluded '$p':" && echo "$hits" | sed 's/^/    /'
done

PUBLIC_COMMIT=$(git commit-tree "$PUBLIC_TREE" -m "$MSG")
echo "full commit   : $FULL_COMMIT ($(git ls-tree -r --name-only "$FULL_COMMIT" | wc -l | tr -d ' ') files)"
echo "public commit : $PUBLIC_COMMIT ($(git ls-tree -r --name-only "$PUBLIC_TREE" | wc -l | tr -d ' ') files)"

if [ "$DRY" = 1 ]; then echo "dry run — nothing pushed"; exit 0; fi

# ---- 3. Push (tokens from ~/.netrc, always masked) ----
token_for() {
  awk -v u="$1" 'BEGIN{IGNORECASE=1} /machine/{c=""} /login/{c=$2} /password/{if(c==u){print $2; exit}}' ~/.netrc
}
push_to() {  # user repo commit
  local user=$1 repo=$2 commit=$3 T
  T=$(token_for "$user")
  [ -z "$T" ] && { echo "no token for $user in ~/.netrc" >&2; return 1; }
  echo "== push → $user/$repo =="
  git -c credential.helper= push -f "https://${user}:${T}@github.com/${user}/${repo}.git" "$commit:refs/heads/main" 2>&1 \
    | sed -E "s/$T/***/g"
  # verify remote head
  local remote
  remote=$(git -c credential.helper= ls-remote "https://${user}:${T}@github.com/${user}/${repo}.git" refs/heads/main 2>/dev/null | cut -f1)
  unset T
  if [ "$remote" = "$commit" ]; then echo "  verified: remote main = $commit"; else echo "  VERIFY FAILED: remote main = ${remote:-?}" >&2; return 1; fi
}

[ "$ONLY" != yonchan ]   && push_to changyeon  jpop-lyrics "$FULL_COMMIT"
[ "$ONLY" != changyeon ] && push_to yonchan123 jpop-lyrics "$PUBLIC_COMMIT"
exit 0
