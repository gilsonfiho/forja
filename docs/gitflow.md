# Git Flow do projeto

## Branches de longa duração

- **`main`** — produção. Só recebe merges de `release/*` e `hotfix/*`. Cada merge gera uma **tag** `vX.Y.Z`.
- **`develop`** — integração. Base das `feature/*` e origem das `release/*`.

## Branches de trabalho

| Prefixo | Origem | Destino | Uso |
| --- | --- | --- | --- |
| `feature/*` | `develop` | `develop` (PR) | Nova funcionalidade (um agent, uma skill...). |
| `release/*` | `develop` | `main` + `develop` | Estabilização, bump de versão, CHANGELOG. |
| `hotfix/*` | `main` | `main` + `develop` | Correção urgente em produção. |

## Ciclo de uma feature

Cada feature entrega uma versão **MINOR** própria: faz o bump de versão, atualiza
o CHANGELOG e recebe uma **tag** na sua merge em `develop`.

```bash
git checkout develop && git pull
git checkout -b feature/<nome>
# ... desenvolve, commita (Conventional Commits) ...
# bump de versão em pyproject.toml + src/forja/__init__.py (ex.: 0.8.0 -> 0.9.0)
# adiciona a seção da versão no CHANGELOG.md
# abre PR feature/<nome> -> develop ; merge com --no-ff
git tag -a vX.Y.0 -m "vX.Y.0 — <feature>"
```

## Ciclo de uma release

```bash
git checkout -b release/X.Y.Z develop
# bump de versão (pyproject + __init__) e atualização do CHANGELOG
git checkout main && git merge --no-ff release/X.Y.Z
git tag -a vX.Y.Z -m "release X.Y.Z"
git checkout develop && git merge --no-ff release/X.Y.Z
git branch -d release/X.Y.Z
```

## Convenção de commits (Conventional Commits)

```
<tipo>(<escopo opcional>): <descrição no imperativo>
```

Tipos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `perf`, `build`.

Exemplos:
- `feat(jira): sincroniza issues do sprint atual`
- `fix(rag): corrige chunking de documentos longos`

> **Regra do projeto:** nenhuma assinatura/atribuição automática de ferramentas
> de IA nos commits ou PRs.

## Versionamento

SemVer (`MAJOR.MINOR.PATCH`). O histórico fica em [`CHANGELOG.md`](../CHANGELOG.md),
no formato *Keep a Changelog*.

- **Feature** → bump de `MINOR`, tag `vX.Y.0` na merge em `develop`.
- **Release** → consolida o conjunto de features, tag `vX.Y.Z` em `main`.
- **Hotfix** → bump de `PATCH`, tag em `main`.

## Helper

Use [`scripts/new_feature.sh`](../scripts/new_feature.sh) para abrir uma feature padronizada.
