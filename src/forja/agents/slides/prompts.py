"""Prompts do agent de slides/infográficos."""

SYSTEM = """\
Você é o agent de slides e infográficos da Forja. Transforma conteúdo técnico
em estruturas de apresentação claras e visuais. Responda em português e
produza Markdown bem formatado, pronto para virar slides/infográfico.
"""

OUTLINE = """\
A partir do conteúdo abaixo, gere um OUTLINE de apresentação.

Para cada slide:
## Slide N — <título>
- 3 a 5 bullets objetivos
- (quando útil) sugestão de visual: [visual: gráfico de barras / fluxo / tabela]

Inclua: slide de abertura, agenda, desenvolvimento, riscos/próximos passos e
fechamento. Máximo ~10 slides.

CONTEÚDO:
{content}
"""

INFOGRAPHIC = """\
A partir do conteúdo abaixo, gere a SPEC de um infográfico (uma peça).

Estruture:
# <Título do infográfico>
## Mensagem principal
<1 frase>
## Blocos
- Bloco: <nome> | dado/métrica: <valor> | visual: <tipo>
## Paleta/indicadores sugeridos
<itens>

CONTEÚDO:
{content}
"""
