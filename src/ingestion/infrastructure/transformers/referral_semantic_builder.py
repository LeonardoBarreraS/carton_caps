from __future__ import annotations

import json

from openai import OpenAI

from ...domain.models import IngestionDocument, RawRecord
from ...domain.ports import IDocumentTransformer

_SPLIT_PROMPT = """\
You are a document segmentation expert for a referral program knowledge base.

Given the full text of a referral program document, identify every distinct semantic unit:
rules, eligibility criteria, reward definitions, FAQ entries, policy sections, deadlines,
or any other self-contained statement a user might ask about.

Each unit must be self-contained — a reader should be able to understand it without needing
to read any other unit.

Return a JSON object with a single key "chunks" containing an array of objects.
Each object must have:
- "chunk_id": sequential integer starting at 1
- "title": the exact section heading or question as it appears in the document (e.g. "#1. Eligibility", "How do I refer a friend?")
- "label": short descriptive label for metadata (e.g., "Eligibility Rule", "FAQ: How to earn points")
- "text": the body content of the chunk only — the heading is NOT repeated here, just the content

Document text:
{text}"""

_MIN_CHUNK_LENGTH = 30  # characters — discard headings-only fragments


class ReferralSemanticBuilder(IDocumentTransformer):
    """Uses an LLM to split a PDF document into semantically self-contained chunks.

    Each PDF record → N IngestionDocuments, one per rule / FAQ / policy section.
    Splitting is driven by meaning, not character count.
    The LLM is instructed to preserve text exactly — no rewriting.
    """

    def __init__(self, openai_client: OpenAI, model: str = "gpt-5.4-mini") -> None:
        self._client = openai_client
        self._model = model

    def transform(self, record: RawRecord) -> list[IngestionDocument]:
        text = record.content["text"]
        filename = record.content["filename"]

        chunks = self._extract_chunks(text)

        return [
            IngestionDocument(
                id=f"{record.id}_{chunk['chunk_id']}",
                text=(chunk.get("title", chunk.get("label", "")) + "\n\n" + chunk["text"]).strip(),
                metadata={
                    "source_file": filename,
                    "chunk_id": chunk["chunk_id"],
                    "title": chunk.get("title", ""),
                    "label": chunk.get("label", "rule"),
                    "source": "referral_program",
                },
            )
            for chunk in chunks
            if len(chunk.get("text", "").strip()) >= _MIN_CHUNK_LENGTH #----->>> OJO ACA PORQUE SOLO ADMITE SEGMENTOS DE TEXTO MAYORES A 30 CARACTERES, SINO, NO LO GUARDA
        ]

    def _extract_chunks(self, text: str) -> list[dict]:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": _SPLIT_PROMPT.format(text=text)}],
            temperature=0.0,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw)
            return parsed.get("chunks", [])
        except json.JSONDecodeError:
            # Fallback: split by double newlines if LLM returned malformed JSON
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            return [
                {"chunk_id": i + 1, "label": "paragraph", "text": p}
                for i, p in enumerate(paragraphs)
            ]
