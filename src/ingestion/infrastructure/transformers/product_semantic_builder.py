from __future__ import annotations

from openai import OpenAI

from ...domain.models import IngestionDocument, RawRecord
from ...domain.ports import IDocumentTransformer

_ENRICHMENT_PROMPT = """\
You are a product catalog labeler for a family grocery shopping assistant.

Given a grocery product, write a semantically rich description for vector search retrieval.
Include: product category, meal occasions it suits, dietary profile keywords (e.g. kid-friendly, \
gluten-free, healthy, high-protein), budget tier (budget-friendly / mid-range / premium based on \
the price), and key attributes relevant to a parent shopping for family groceries.

Be concise (3-5 sentences). Do not invent nutritional facts not implied by the product info.
Only label what can be reasonably inferred.

Product:
Name: {name}
Description: {description}
Price: ${price:.2f}

Output only the enriched description text. No headers, no bullet points."""


class ProductSemanticBuilder(IDocumentTransformer):
    """Calls an LLM to produce a semantically enriched document for each product row.

    Each product row → exactly one IngestionDocument.
    The enriched text adds inferred labels (category, occasion, dietary profile, budget tier)
    that make the raw structured row a strong embedding target.
    """

    def __init__(self, openai_client: OpenAI, model: str = "gpt-5.4-mini") -> None:
        self._client = openai_client
        self._model = model

    def transform(self, record: RawRecord) -> list[IngestionDocument]:
        content = record.content
        prompt = _ENRICHMENT_PROMPT.format(
            name=content["name"],
            description=content["description"] or "No description provided.",
            price=content["price"],
        )

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        enriched_text = response.choices[0].message.content.strip()

        return [
            IngestionDocument(
                id=f"product_{record.id}",
                text=f"{content['name']}. Price: ${content['price']:.2f}. {enriched_text}",
                metadata={
                    "product_id": record.id,
                    "name": content["name"],
                    "price": content["price"],
                    "source": "product_catalog"
                },
            )
        ]
