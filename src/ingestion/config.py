from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{name}' is not set. "
            f"Copy .env.example to .env and fill in the values."
        )
    return value


OPENAI_API_KEY: str = _require("OPENAI_API_KEY")

# Path to the SQLite database containing the product catalog
SQLITE_DB_PATH: str = os.environ.get(
    "SQLITE_DB_PATH", str(Path(__file__).parent.parent.parent / "data" / "carton_caps_data.sqlite")
)

# Qdrant vector store API URL
QDRANT_URL: str = os.environ.get("QDRANT_URL", "http://localhost:6333")

# Qdrant API key (required for cloud/secured instances, optional for local)
QDRANT_API_KEY: str | None = os.environ.get("QDRANT_API_KEY") or None

# Directory containing the referral program PDF documents
PDF_DOCS_DIR: str = os.environ.get(
    "PDF_DOCS_DIR", str(Path(__file__).parent.parent.parent / "data" / "docs")
)

# Directory where ChromaDB will persist the vector store
VECTOR_STORE_PATH: str = os.environ.get(
    "VECTOR_STORE_PATH", str(Path(__file__).parent.parent.parent / "data" / "vector_store")
)
