#!/usr/bin/env bash
# Abre uma nova feature seguindo o git flow do projeto.
#   uso: scripts/new_feature.sh <nome-da-feature>
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "uso: $0 <nome-da-feature>" >&2
  exit 1
fi

name="$1"
branch="feature/${name}"

git checkout develop
git pull --ff-only || true
git checkout -b "${branch}"

echo "Branch ${branch} criada a partir de develop."
echo "Ao terminar: commit (Conventional Commits) e abra PR -> develop."
