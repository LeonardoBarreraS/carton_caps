from __future__ import annotations

import re
from pathlib import Path

import pdfplumber

from ...domain.models import RawRecord
from ...domain.ports import IKnowledgeSource


class PDFReferralSource(IKnowledgeSource):
    """Reads all PDF files from the docs directory.

    Returns one RawRecord per PDF. Each record carries the full extracted
    text of the document — the transformer is responsible for semantic splitting.
    """

    def __init__(self, docs_dir: str) -> None:
        self._docs_dir = Path(docs_dir)

    def load(self) -> list[RawRecord]:
        pdf_files = sorted(self._docs_dir.glob("*.pdf"))
        return [
            RawRecord(
                id=pdf_path.stem,
                content={
                    "filename": pdf_path.name,
                    "text": self._extract_text(pdf_path),
                },
            )
            for pdf_path in pdf_files
        ]

    def _extract_text(self, pdf_path: Path) -> str:
        pages: list[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text.strip())
        raw = "\n\n".join(pages)
        # Collapse runs of 3+ blank lines into a single blank line
        return re.sub(r"\n{3,}", "\n\n", raw).strip()
