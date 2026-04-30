# Carton Caps Conversational Assistant

An AI-powered conversational assistant for the **Carton Caps** school fundraising platform. It helps parents discover products, understand the referral program, and stay engaged — all through natural conversation.

Built with **FastAPI**, **LangGraph**, **OpenAI**, and **Qdrant**, following Domain-Driven Design and Clean Architecture.

---

## Prerequisites

- **Python 3.11+**
- **Qdrant** running locally (`http://localhost:6333`) or a Qdrant Cloud instance
- **OpenAI API key**

## Quick Start

```bash
# 1. Clone the repo and enter the project directory
cd app_solution

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY and QDRANT_URL

# 5. Run the ingestion pipeline (loads products & referral docs into Qdrant)
python -m src.ingestion

# 6. Start the API server
uvicorn main:app --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

---

## Gradio UI (Demo Frontend)

A Gradio-based chat interface is included under `gradio_app/` for showcasing the assistant.

```bash
# Install Gradio dependencies
pip install -r gradio_app/requirements.txt

# Start the UI (requires the API to be running on port 8000)
python gradio_app/app.py
```

Open `http://localhost:7860` in your browser to interact with the assistant.

---

## Project Structure

```
main.py                  # FastAPI entry point
requirements.txt         # Runtime dependencies
.env.example             # Environment variable template
data/                    # SQLite databases and PDF documents
gradio_app/              # Gradio demo frontend
src/
  ├── ingestion/         # Data ingestion pipeline (products + referral rules → Qdrant)
  ├── knowledge_retrieval/  # RAG retrieval layer
  ├── conversation_management/  # Conversation orchestration and state
  ├── decision_intelligence/    # Intent classification and response strategy
  └── shell/             # API routes and dependency wiring (composition root)
system_design/           # Full design documentation (see below)
```

---

## System Design Documentation

The `system_design/` folder contains the complete design process, organized into sequential phases. **Each phase has a summary file** that gives a concise overview — start there.

| Phase | Summary File | What It Covers |
|-------|-------------|----------------|
| 0 | `problem_understanding_summary.md` | Business context, actors, and system purpose |
| 1 | `requirements_summary.md` | Functional requirements and system workflows |
| 2 | `domain_modeling_summary.md` | Domain concepts, process entities, invariants, and bounded contexts |
| 3 | `architecture_summary.md` | Component mapping, layered architecture, and context communication |
| 4 | `domain_model_layer_summary.md` | Domain model materialization (entities, value objects, aggregates) |
| 5 | `application_layer_design_summary.md` | Use cases, workflow orchestration, and context coordination |
| 6 | `infrastructure_layer_summary.md` | Adapters, repositories, event bus, and API entry points |
| 7 | `shell_composition_layer_summary.md` | Dependency wiring, context wiring, and system composition |

Reading these summaries in order gives a full picture of how and why the system is designed the way it is.

---

## Environment Variables

See `.env.example` for the full list. The key ones:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `QDRANT_URL` | Yes | Qdrant instance URL |
| `QDRANT_API_KEY` | No | Only needed for Qdrant Cloud |
| `LLM_MODEL` | No | Defaults to `gpt-5.4-mini` |

---

## License

This project was built as part of a technical assessment.
