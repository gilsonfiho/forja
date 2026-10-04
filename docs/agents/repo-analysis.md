# Agent: Repo Analysis

Varre e analisa os diversos repositórios de serviços/projetos.

## Ações

- `scan` (default): inventário de todos os repos sob `WORKG_REPOS_ROOT`
  (branch atual, último commit, remotes, stack, CI, testes, README, estado dirty)
  e um resumo de riscos (sem CI, sem testes, com alterações não commitadas).
- `analyze`: análise de saúde (LLM) de um repositório específico com recomendações.

## Parâmetros

- `root`: raiz onde estão os repositórios (default: `WORKG_REPOS_ROOT`).
- `max_depth`: profundidade da busca (default 3).
- `name`: nome do repositório (para `analyze`).

## Exemplos

```bash
workg run repo-analysis --action scan
workg run repo-analysis --action analyze -p name=meu-servico
```

Detecção de stack por marcadores (`pyproject.toml`, `package.json`, `go.mod`,
`Dockerfile`, …) e de CI (`.github/workflows`, `.gitlab-ci.yml`, `Jenkinsfile`, …).
