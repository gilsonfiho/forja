# Contribuindo

## Ambiente

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate       # Linux/macOS
pip install -e ".[dev,all]"
pre-commit install
```

## Antes de commitar

```bash
ruff format .
ruff check . --fix
mypy
pytest
```

(ou simplesmente `pre-commit run --all-files`).

## Padrões

- **Git Flow** e **Conventional Commits** — ver [`docs/gitflow.md`](docs/gitflow.md).
- Toda feature entra por `feature/*` com PR para `develop`.
- Atualize o `CHANGELOG.md` (seção `Unreleased`) na mesma PR.
- **Nunca** inclua assinatura/atribuição automática de IA em commits ou PRs.

## Testes

Cobertura mínima esperada para novos módulos; use `pytest --cov=forja`.
