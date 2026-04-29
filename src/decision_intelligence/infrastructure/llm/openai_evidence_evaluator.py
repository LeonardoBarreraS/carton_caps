from __future__ import annotations

import json

from openai import OpenAI

from decision_intelligence.application.ports.i_evidence_evaluator import IEvidenceEvaluator
from decision_intelligence.domain.value_objects.retrieval_query import RetrievalQuery
from decision_intelligence.domain.value_objects.retrieved_evidence import RetrievedEvidence

_EVALUATION_PROMPT = """\
You are a retrieval quality evaluator for a RAG pipeline in a grocery shopping assistant.

Evaluate the retrieved evidence chunks against the retrieval query below.

Query: {query_text}

Retrieved chunks:
{chunks_text}

Score both dimensions and return a JSON object with these exact fields:

- context_recall_score (float 0.0–1.0): Does the retrieved evidence cover all of the \
query's information needs?
  0.0 = none of the query's needs are covered by any chunk
  1.0 = all information needs are addressed by the retrieved chunks

- context_precision_score (float 0.0–1.0): Are the retrieved chunks tightly relevant \
to the query (vs. noise)?
  0.0 = all chunks are unrelated noise
  1.0 = every chunk directly supports answering the query

Return only a valid JSON object."""


class OpenAIEvidenceEvaluator(IEvidenceEvaluator):
    """
    Implements IEvidenceEvaluator using OpenAI gpt-4o-mini in JSON mode.
    Scores retrieved evidence for context recall and precision.
    Returns a new immutable RetrievedEvidence with updated scores.
    These scores drive the retrieval retry cycle in DecisionIntelligenceSubgraph.
    """

    def __init__(self, openai_client: OpenAI, model: str = "gpt-5.4-mini") -> None:
        self._client = openai_client
        self._model = model

    def evaluate(
        self,
        query: RetrievalQuery,
        evidence: RetrievedEvidence,
    ) -> RetrievedEvidence:
        chunks_text = "\n".join(
            f"{i + 1}. {chunk.text}" for i, chunk in enumerate(evidence.chunks)
        )
        prompt = _EVALUATION_PROMPT.format(
            query_text=query.query_text,
            chunks_text=chunks_text,
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                timeout=30.0,
            )
            raw = response.choices[0].message.content.strip()
            scores = json.loads(raw)
            recall = max(0.0, min(1.0, float(scores.get("context_recall_score", 0.0))))
            precision = max(0.0, min(1.0, float(scores.get("context_precision_score", 0.0))))
        except (json.JSONDecodeError, ValueError, TypeError, Exception):
            recall = 0.0
            precision = 0.0

        return RetrievedEvidence.create(
            source_target=evidence.source_target,
            chunks=list(evidence.chunks),
            context_recall_score=recall,
            context_precision_score=precision,
        )
