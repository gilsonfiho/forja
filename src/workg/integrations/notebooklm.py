"""Adapter para o NotebookLM (slides / infográficos).

O NotebookLM não expõe uma API pública estável. Este adapter prepara um
**pacote de fontes** consolidado (Markdown) pronto para ser carregado no
NotebookLM, e documenta o passo de geração (que hoje é feito pela interface
web). Quando/se uma automação de navegador for habilitada, ela pode ser
plugada em :meth:`generate`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from workg.config import Settings
from workg.logging_conf import get_logger

log = get_logger("notebooklm")

UPLOAD_INSTRUCTIONS = """\
1. Abra o NotebookLM (https://notebooklm.google.com/).
2. Crie/abra um notebook e faça upload do arquivo de fontes gerado.
3. Use "Audio Overview" / "Slides" / "Infographic" para gerar o material.
4. Ajuste o prompt de foco conforme o objetivo do material.
"""


@dataclass(slots=True)
class SourcePackage:
    path: Path
    title: str
    chars: int


class NotebookLMAdapter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def enabled(self) -> bool:
        return bool(self.settings.notebooklm_enabled)

    def prepare_source(self, title: str, content: str, out_dir: Path) -> SourcePackage:
        """Grava um arquivo de fontes consolidado para upload no NotebookLM."""
        out_dir.mkdir(parents=True, exist_ok=True)
        safe = title.strip().replace("/", "-") or "fonte"
        path = out_dir / f"notebooklm-source-{safe}.md"
        path.write_text(content, encoding="utf-8")
        log.info("notebooklm.source", path=str(path), chars=len(content))
        return SourcePackage(path=path, title=title, chars=len(content))

    def generate(self, package: SourcePackage) -> dict[str, object]:
        """Gera o material no NotebookLM.

        Enquanto não houver automação habilitada, retorna o pacote de fontes
        e as instruções de geração manual.
        """
        if not self.enabled:
            return {
                "mode": "manual",
                "source": str(package.path),
                "instructions": UPLOAD_INSTRUCTIONS,
                "notebook_id": self.settings.notebooklm_notebook_id,
            }
        # Ponto de extensão para automação (browser/API) futura.
        return {
            "mode": "automation_not_implemented",
            "source": str(package.path),
            "notebook_id": self.settings.notebooklm_notebook_id,
        }
