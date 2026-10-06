# Agent: Commit / PR / DevOps

Gera bons padrões de commit, descrições de PR e artefatos de DevOps.

## Ações

- `commit` (default): mensagem **Conventional Commits** a partir do diff staged
  (ou de um diff/`repo` informado).
- `pr`: descrição de PR estruturada a partir dos commits em `base..head`.
- `devops`: padrões/artefatos de DevOps (CI, branching, pre-commit, segurança)
  para uma stack.

## Parâmetros

- `repo`: caminho do repositório (default `.`).
- `diff`: diff explícito (senão usa `git diff --staged`).
- `base` / `head`: faixa de commits para a PR (default `develop`..`HEAD`).
- `commits`: lista de commits explícita.
- `stack`: stack para `devops` (default `python`).

## Exemplos

```bash
git add -A
forja run commit-pr-devops --action commit
forja run commit-pr-devops --action pr -p base=develop -p head=HEAD
forja run commit-pr-devops --action devops -p stack=node --prompt "deploy em container"
```

> As saídas **nunca** incluem assinatura/atribuição de ferramentas de IA.
