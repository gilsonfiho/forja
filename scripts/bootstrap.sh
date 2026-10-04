#!/usr/bin/env bash
# Bootstrap do ambiente de desenvolvimento (Linux/macOS)
set -euo pipefail

echo "==> Criando venv (.venv)"
python3 -m venv .venv

echo "==> Ativando venv"
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Atualizando pip e instalando dependências (dev)"
python -m pip install --upgrade pip
pip install -e ".[dev]"

if [ ! -f .env ]; then
  echo "==> Criando .env a partir de .env.example"
  cp .env.example .env
fi

echo "==> Instalando hooks de pre-commit"
pre-commit install

echo
echo "Pronto. Rode:  workg serve  (ou: uvicorn workg.web.app:app --reload)"
