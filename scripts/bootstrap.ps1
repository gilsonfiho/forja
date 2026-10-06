# Bootstrap do ambiente de desenvolvimento (Windows / PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "==> Criando venv (.venv)"
python -m venv .venv

Write-Host "==> Ativando venv"
. .\.venv\Scripts\Activate.ps1

Write-Host "==> Atualizando pip e instalando dependências (dev)"
python -m pip install --upgrade pip
pip install -e ".[dev]"

if (-not (Test-Path ".env")) {
    Write-Host "==> Criando .env a partir de .env.example"
    Copy-Item ".env.example" ".env"
}

Write-Host "==> Instalando hooks de pre-commit"
pre-commit install

Write-Host "`nPronto. Rode:  forja serve  (ou: uvicorn forja.web.app:app --reload)"
