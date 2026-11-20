#!/bin/bash
# Bring GitHub, this machine and the Longleaf checkout to the same state.
# 1. pull GitHub main here and push local commits (refuses with uncommitted changes);
# 2. fast-forward the Longleaf checkout tapestry-all/tapestry to the same commit;
# 3. copy git-ignored data and outputs to the same paths on Longleaf, never replacing
#    a newer Longleaf file. Longleaf keeps run caches the laptop never needs, so
#    nothing is copied back.
# Campaign folders on Longleaf are not git checkouts: bring their code, problems and
# experiment records into main by hand (see AGENTS.md).
#
#   scripts/sync_longleaf.sh            # everything
#   scripts/sync_longleaf.sh --git      # commits only
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
host=${LONGLEAF:-longleaf}
remote=/hickory/proj/jlessler/projects/tapestry-all/tapestry
paths=(data production/output output sandbox references)

if [ -n "$(git status --porcelain --untracked-files=normal -- . ':!.claude')" ]; then
    git status --short -- . ':!.claude'
    echo 'Commit or discard these changes first.' >&2
    exit 1
fi
git pull --ff-only -q origin main
git push -q origin main
ssh "$host" "cd $remote && git fetch -q origin && git merge --ff-only -q origin/main && git log -1 --oneline"
[ "${1:-}" = --git ] && exit 0

for p in "${paths[@]}"; do
    [ -d "$p" ] || continue
    echo "== $p"
    rsync -a --update --exclude .DS_Store --exclude __pycache__ "$p/" "$host:$remote/$p/"
done
