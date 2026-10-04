"""Prompts do agent de commit/PR/DevOps."""

SYSTEM = """\
Você é o agent de padrões de engenharia da WorkG. Produz mensagens de commit,
descrições de PR e artefatos de DevOps seguindo boas práticas. Seja conciso,
técnico e consistente. Responda sempre em português.

Regra inviolável: NUNCA inclua assinatura/atribuição de ferramentas de IA
(ex.: "Co-Authored-By: Claude", "Generated with ...") nas saídas.
"""

COMMIT_TEMPLATE = """\
Gere UMA mensagem de commit no padrão Conventional Commits para o diff abaixo.

Formato:
  <tipo>(<escopo opcional>): <descrição imperativa, <= 72 chars>

  <corpo opcional explicando o "porquê", em bullets quando útil>

Tipos válidos: feat, fix, docs, refactor, test, chore, ci, perf, build.
Contexto adicional: {context}

DIFF:
{diff}

Responda apenas com a mensagem de commit, sem cercas de código.
"""

PR_TEMPLATE = """\
Gere uma descrição de Pull Request a partir dos commits abaixo ({base}..{head}).

Estrutura:
## Resumo
<2-4 linhas>

## Mudanças
- <bullets agrupados por tipo>

## Como testar
- <passos>

## Checklist
- [ ] Testes
- [ ] Docs/CHANGELOG
- [ ] Sem segredos

Contexto adicional: {context}

COMMITS:
{commits}
"""

DEVOPS_TEMPLATE = """\
Proponha padrões/artefatos de DevOps para um projeto com a stack: {stack}.

Entregue, quando aplicável:
- pipeline de CI (lint, testes, build) descrito e, se pedido, em YAML;
- estratégia de branching/versionamento compatível com git flow + SemVer;
- hooks de pre-commit recomendados;
- pontos de atenção de segurança (segredos, dependências).

Objetivo específico: {context}
"""
