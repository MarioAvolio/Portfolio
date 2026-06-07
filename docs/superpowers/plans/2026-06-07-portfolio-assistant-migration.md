# Portfolio Assistant Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename and repurpose the `insurellm` microservice into `portfolio-assistant` — a RAG chatbot grounded in Mario Avolio's real professional profile (bio, skills, projects, experience, publications).

**Architecture:** The service keeps its existing stack (LangChain + Chroma + OpenAI) and all conventions from CONVENTIONS.md unchanged. Only the service name, API prefix, system prompt, and knowledge-base content change. The gateway registry and docker-compose are updated to reference the new name. The Chroma vector DB is cleared so it is rebuilt against the new knowledge base on first query.

**Tech Stack:** Python 3.11, FastAPI, LangChain, ChromaDB, OpenAI (gpt-4.1-nano + text-embedding-3-small), uv, pytest

**Working directory:** `C:\Users\ma.avolio\Documents\GitHub\Portfolio`

---

## File Map

### Modified (service internals — after rename)
| File | Change |
|---|---|
| `services/portfolio-assistant/pyproject.toml` | name, description, env-var comment |
| `services/portfolio-assistant/src/backend/__main__.py` | docstring |
| `services/portfolio-assistant/src/backend/webserver/configs/configs.py` | `app_name`, `api_prefix` defaults + docstrings |
| `services/portfolio-assistant/src/backend/webserver/configs/files/local.yml` | `app_name`, `api_prefix`, header comment |
| `services/portfolio-assistant/src/backend/ai/llm/rag.py` | system prompt |
| `services/portfolio-assistant/src/backend/webserver/services/rag_service.py` | docstring |
| `services/portfolio-assistant/src/backend/webserver/routers/query.py` | docstring |
| `services/portfolio-assistant/test/test_probes.py` | PREFIX constant, app_name assertion |
| `services/portfolio-assistant/test/test_ops.py` | PREFIX constant |

### Modified (external)
| File | Change |
|---|---|
| `gateway/src/backend/webserver/configurations.py` | `_URL_ENV` key: `insurellm` → `portfolio-assistant` |
| `gateway/src/backend/webserver/configs/files/local.yml` | service entry: name, description, query_path, query_example |
| `docker-compose.yml` | env var `INSURELLM_URL` → `PORTFOLIO_ASSISTANT_URL`, comment |
| `docs/ARCHITECTURE.md` | table row + comment |

### Deleted (old KB)
- `services/portfolio-assistant/assets/knowledge-base/company/` (all files)
- `services/portfolio-assistant/assets/knowledge-base/contracts/` (all files)
- `services/portfolio-assistant/assets/knowledge-base/employees/` (all files)
- `services/portfolio-assistant/assets/knowledge-base/products/` (all files)
- `services/portfolio-assistant/assets/vector_db/` (entire dir — rebuilt on first query)

### Created (new KB)
```
services/portfolio-assistant/assets/knowledge-base/
  profile/bio.md
  profile/contact.md
  skills/tech-stack.md
  skills/specializations.md
  projects/ai-microservices-hub.md
  projects/future-work.md
  experience/machine-learning-reply.md
  experience/research-fellow.md
  education/msc-bicocca.md
  education/bsc-calabria.md
  publications/iciap-2025.md
  publications/kr-2023.md
```

---

## Task 1: Rename the service directory

**Files:**
- Rename: `services/insurellm/` → `services/portfolio-assistant/`

- [ ] **Step 1: git mv to preserve history**

```powershell
git mv services/insurellm services/portfolio-assistant
```

Expected output: no error, directory renamed.

- [ ] **Step 2: Verify rename**

```powershell
git status
```

Expected: `renamed: services/insurellm/... -> services/portfolio-assistant/...` for every file.

- [ ] **Step 3: Commit the rename alone**

```powershell
git add -A
git commit -m "refactor(insurellm): rename service directory to portfolio-assistant"
```

---

## Task 2: Update service identity (pyproject + configs)

**Files:**
- Modify: `services/portfolio-assistant/pyproject.toml`
- Modify: `services/portfolio-assistant/src/backend/webserver/configs/configs.py`
- Modify: `services/portfolio-assistant/src/backend/webserver/configs/files/local.yml`

- [ ] **Step 1: Update pyproject.toml**

Replace the entire file content with:

```toml
[project]
name = "portfolio-assistant"
version = "0.1.0"
description = "RAG microservice answering questions about Mario Avolio's professional portfolio, grounded in a local knowledge base."
readme = "readme.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "pydantic>=2.7",
    "httpx>=0.27",
    "pyyaml>=6.0",
    "langchain-core>=0.3",
    "langchain-community>=0.3",
    "langchain-chroma>=0.2",
    "langchain-openai>=0.3",
    "langchain-text-splitters>=0.3",
    "chromadb>=0.5",
    "tqdm>=4.66",
]

# Optional local-embeddings backend (PORTFOLIO_ASSISTANT_EMBEDDINGS=hf). Heavy (torch);
# install with: uv sync --extra hf
[project.optional-dependencies]
hf = [
    "langchain-huggingface>=0.1",
    "sentence-transformers>=3.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.6",
    "mypy>=1.8",
    "types-pyyaml>=6.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/backend"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["test"]

[tool.ruff]
line-length = 100
src = ["src", "test"]
extend-exclude = ["src/backend/ai"]

[tool.mypy]
python_version = "3.11"
files = ["src/backend"]
ignore_missing_imports = true
exclude = ['src/backend/ai/']
```

- [ ] **Step 2: Update configs.py defaults**

In `services/portfolio-assistant/src/backend/webserver/configs/configs.py`, replace the `Configs` class default values:

```python
"""Configuration models for the portfolio-assistant service."""

from pydantic import BaseModel, Field


class RagConfig(BaseModel):
    """Tuning knobs for the RAG pipeline.

    Attributes:
        embeddings: Embeddings backend, ``openai`` (default) or ``hf`` (local).
        chunking: Chunking strategy, ``simple`` (default) or ``llm``.
        max_documents: Optional cap on indexed documents (``None`` = all).
    """

    embeddings: str = "openai"
    chunking: str = "simple"
    max_documents: int | None = None


class Configs(BaseModel):
    """Top-level configuration for the portfolio-assistant RAG service.

    Attributes:
        app_name: Logical service name.
        version: Service version surfaced by the status endpoint.
        environment: Short environment label.
        api_prefix: Base URL prefix shared by the functional routers.
        model_name: Chat model used by the RAG generation step.
        rag: RAG pipeline tuning block.
    """

    app_name: str = "portfolio-assistant"
    version: str = "0.1.0"
    environment: str = "local"
    api_prefix: str = "/portfolio-assistant/api/v1"
    model_name: str = "gpt-4.1-nano"
    rag: RagConfig = Field(default_factory=RagConfig)
```

- [ ] **Step 3: Update local.yml**

Replace `services/portfolio-assistant/src/backend/webserver/configs/files/local.yml`:

```yaml
# portfolio-assistant configuration for the local environment.
# Non-secret values only. OPENAI_API_KEY is read from the environment.
app_name: portfolio-assistant
api_prefix: /portfolio-assistant/api/v1
model_name: gpt-4.1-nano

rag:
  # Embeddings backend: "openai" (light, default) or "hf" (local, needs the hf extra).
  embeddings: openai
  # Chunking strategy: "simple" (free, default) or "llm" (richer, one call per doc).
  chunking: simple
  # Optional cap on indexed documents (null = all).
  max_documents: null
```

- [ ] **Step 4: Commit**

```powershell
git add services/portfolio-assistant/pyproject.toml `
        services/portfolio-assistant/src/backend/webserver/configs/configs.py `
        services/portfolio-assistant/src/backend/webserver/configs/files/local.yml
git commit -m "refactor(portfolio-assistant): update service identity in configs"
```

---

## Task 3: Update system prompt

**Files:**
- Modify: `services/portfolio-assistant/src/backend/ai/llm/rag.py`

- [ ] **Step 1: Replace system prompt**

In `rag.py`, replace the `_system_prompt` string (lines 12-19):

```python
        self._system_prompt = """
                                You are a knowledgeable assistant for Mario Avolio's professional portfolio.
                                You help recruiters, collaborators, and visitors learn about Mario's
                                background, skills, projects, experience, education, and publications.
                                Answer questions about Mario concisely and accurately.
                                If relevant, use the given context to answer any question.
                                If you don't know the answer, say so.
                                Context:
                                {context}
                                """
```

- [ ] **Step 2: Commit**

```powershell
git add services/portfolio-assistant/src/backend/ai/llm/rag.py
git commit -m "refactor(portfolio-assistant): update RAG system prompt for portfolio domain"
```

---

## Task 4: Update docstrings

**Files:**
- Modify: `services/portfolio-assistant/src/backend/__main__.py`
- Modify: `services/portfolio-assistant/src/backend/webserver/services/rag_service.py`
- Modify: `services/portfolio-assistant/src/backend/webserver/routers/query.py`

- [ ] **Step 1: Update __main__.py docstring**

Line 1, replace:
```python
"""Application entrypoint and FastAPI app factory for the portfolio-assistant service."""
```

Line 32, replace `get_app` docstring body:
```python
    """Builds and returns the configured portfolio-assistant application."""
```

- [ ] **Step 2: Update rag_service.py docstring**

Line 1 module docstring, replace:
```python
"""Business logic for the portfolio-assistant RAG service.

The heavyweight RAG pipeline (LangChain, Chroma, embeddings, OpenAI) is imported
and built **lazily** on the first query and cached thereafter. This keeps the
app — and the probe tests — importable without the ML stack, and lets the
service degrade gracefully (``503``) when it is not configured.
"""
```

Line 16 class docstring:
```python
    """Answers questions against Mario Avolio's portfolio knowledge base."""
```

- [ ] **Step 3: Update query.py docstring**

Inside `query()`, replace the docstring:
```python
    """Answers a question against Mario Avolio's portfolio knowledge base.

    Raises:
        RagUnavailableError: Translated to ``503`` when the pipeline is not
            configured (e.g. missing ``OPENAI_API_KEY``).
    """
```

- [ ] **Step 4: Commit**

```powershell
git add services/portfolio-assistant/src/backend/__main__.py `
        services/portfolio-assistant/src/backend/webserver/services/rag_service.py `
        services/portfolio-assistant/src/backend/webserver/routers/query.py
git commit -m "refactor(portfolio-assistant): update docstrings for portfolio domain"
```

---

## Task 5: Update tests

**Files:**
- Modify: `services/portfolio-assistant/test/test_probes.py`
- Modify: `services/portfolio-assistant/test/test_ops.py`

- [ ] **Step 1: Update test_probes.py**

Replace file content:

```python
"""Operational probe tests.

These exercise the microservice surface (app factory, routers, configuration)
without touching the heavyweight RAG pipeline, so they run anywhere at zero
cost. End-to-end RAG answers require the full environment and an API key.
"""

from fastapi.testclient import TestClient

PREFIX = "/portfolio-assistant/api/v1"


def test_ping(client: TestClient) -> None:
    assert client.get("/ping").json() == "Alive"


def test_health(client: TestClient) -> None:
    assert client.get(f"{PREFIX}/health").json() == {"health": "OK"}


def test_status_reports_metadata(client: TestClient) -> None:
    body = client.get(f"{PREFIX}/status").json()
    assert body["app_name"] == "portfolio-assistant"
    assert "model" in body
```

- [ ] **Step 2: Update test_ops.py**

Replace file content:

```python
"""Readiness and request-id tests."""

from fastapi.testclient import TestClient

PREFIX = "/portfolio-assistant/api/v1"


def test_ready(client: TestClient) -> None:
    response = client.get(f"{PREFIX}/ready")
    assert response.status_code == 200
    assert response.json() == {"ready": True}


def test_request_id_is_echoed(client: TestClient) -> None:
    response = client.get("/ping")
    assert response.headers.get("X-Request-ID")
```

- [ ] **Step 3: Run tests to verify they pass**

```powershell
cd services/portfolio-assistant
uv run pytest test/test_probes.py test/test_ops.py -v
```

Expected: all 5 tests pass (ping, health, status, ready, request_id).

- [ ] **Step 4: Commit**

```powershell
cd ../..
git add services/portfolio-assistant/test/test_probes.py `
        services/portfolio-assistant/test/test_ops.py
git commit -m "test(portfolio-assistant): update test prefix and assertions"
```

---

## Task 6: Update gateway

**Files:**
- Modify: `gateway/src/backend/webserver/configurations.py`
- Modify: `gateway/src/backend/webserver/configs/files/local.yml`

- [ ] **Step 1: Update _URL_ENV in configurations.py**

In `gateway/src/backend/webserver/configurations.py`, replace the `_URL_ENV` dict (lines 21-25):

```python
_URL_ENV = {
    "text-intelligence": "TEXT_INTELLIGENCE_URL",
    "portfolio-assistant": "PORTFOLIO_ASSISTANT_URL",
    "deep-research": "DEEP_RESEARCH_URL",
}
```

- [ ] **Step 2: Update gateway local.yml service entry**

In `gateway/src/backend/webserver/configs/files/local.yml`, replace the `insurellm` service block:

```yaml
  - name: portfolio-assistant
    description: RAG chatbot answering questions about Mario Avolio's professional profile.
    base_url: http://localhost:5001
    health_path: /ping
    query_path: /portfolio-assistant/api/v1/query
    query_example:
      question: What technologies does Mario know?
```

- [ ] **Step 3: Run gateway probe tests**

```powershell
cd gateway
uv run pytest test/ -v
```

Expected: all gateway tests pass.

- [ ] **Step 4: Commit**

```powershell
cd ..
git add gateway/src/backend/webserver/configurations.py `
        gateway/src/backend/webserver/configs/files/local.yml
git commit -m "refactor(gateway): point registry at portfolio-assistant"
```

---

## Task 7: Update docker-compose and docs

**Files:**
- Modify: `docker-compose.yml`
- Modify: `docs/ARCHITECTURE.md`

- [ ] **Step 1: Update docker-compose.yml**

Replace the gateway environment block:

```yaml
services:
  gateway:
    build: ./gateway
    ports:
      - "8000:8000"
    environment:
      ENVIRONMENT: local
      TEXT_INTELLIGENCE_URL: http://text-intelligence:5000
      PORTFOLIO_ASSISTANT_URL: http://portfolio-assistant:5001
      DEEP_RESEARCH_URL: http://deep-research:5002
    depends_on:
      - text-intelligence

  text-intelligence:
    build: ./services/text-intelligence
    ports:
      - "5000:5000"
    environment:
      ENVIRONMENT: local
```

Also update the header comment line:
```yaml
# Default `docker compose up` brings the gateway and the lightweight,
# zero-cost text-intelligence service. The heavyweight services (portfolio-assistant,
# deep-research) require API keys and large images, so they run locally —
```

- [ ] **Step 2: Update ARCHITECTURE.md**

In `docs/ARCHITECTURE.md`, update the components table row and topology diagram:

Components table — replace `insurellm` row:
```markdown
| `portfolio-assistant` | 5001 | RAG chatbot over Mario Avolio's professional profile |
```

Topology diagram — replace `insurellm` with `portfolio-assistant`.

Cost & degradation section — replace mention:
```markdown
`portfolio-assistant` and `deep-research` perform real model calls and require an `OPENAI_API_KEY`
```

- [ ] **Step 3: Commit**

```powershell
git add docker-compose.yml docs/ARCHITECTURE.md
git commit -m "chore: rename insurellm -> portfolio-assistant in compose and docs"
```

---

## Task 8: Replace knowledge base

**Files:**
- Delete: `services/portfolio-assistant/assets/knowledge-base/company/`
- Delete: `services/portfolio-assistant/assets/knowledge-base/contracts/`
- Delete: `services/portfolio-assistant/assets/knowledge-base/employees/`
- Delete: `services/portfolio-assistant/assets/knowledge-base/products/`
- Delete: `services/portfolio-assistant/assets/vector_db/` (if exists)
- Create: 12 new markdown files under `assets/knowledge-base/`

- [ ] **Step 1: Delete old knowledge base and vector DB**

```powershell
$base = "services/portfolio-assistant/assets"
Remove-Item -Recurse -Force "$base/knowledge-base/company"
Remove-Item -Recurse -Force "$base/knowledge-base/contracts"
Remove-Item -Recurse -Force "$base/knowledge-base/employees"
Remove-Item -Recurse -Force "$base/knowledge-base/products"
if (Test-Path "$base/vector_db") { Remove-Item -Recurse -Force "$base/vector_db" }
```

- [ ] **Step 2: Create profile/bio.md**

```markdown
# Mario Avolio — Professional Bio

Mario Avolio is an AI & Cloud Engineer based in Milan, Italy, specialising in building
production-ready AI systems — from agentic workflows to cloud deployment.

His engineering profile spans the full AI lifecycle: research foundations in computer
vision and model optimisation, and industry experience designing and shipping generative
AI applications at enterprise scale.

He currently works as a Machine Learning Engineer at Machine Learning Reply, where he
builds agentic workflows, RAG pipelines, and LLM automation. Before that he was a
Research Fellow at the Imaging & Vision Lab of the University of Milano-Bicocca, where
his work on underwater mine detection won Best Paper at ICIAP 2025.

Mario holds an MSc in Computer Science (Machine Learning track) from the University of
Milano-Bicocca and a BSc in Computer Science from the University of Calabria.
```

Create at: `services/portfolio-assistant/assets/knowledge-base/profile/bio.md`

- [ ] **Step 3: Create profile/contact.md**

```markdown
# Mario Avolio — Contact & Links

- Email: marioavolio@protonmail.com
- LinkedIn: linkedin.com/in/MarioAvolio
- GitHub: github.com/MarioAvolio
- Portfolio website: marioavolio.netlify.app
- Location: Milan, Italy

Mario is open to select opportunities in AI engineering, agentic systems, and
cloud/MLOps roles.
```

Create at: `services/portfolio-assistant/assets/knowledge-base/profile/contact.md`

- [ ] **Step 4: Create skills/tech-stack.md**

```markdown
# Mario Avolio — Tech Stack

## Programming Languages
- Python (primary language across all projects)

## AI / ML Frameworks
- PyTorch — deep learning model training and fine-tuning
- LangChain — LLM orchestration, RAG pipelines, tool use
- OpenAI Agents SDK — agentic workflow construction

## Cloud & DevOps
- Docker and Docker Compose — containerisation and local orchestration
- FastAPI — production API services
- Azure — cloud infrastructure for generative AI solutions
- GitHub Actions — CI/CD pipelines
- Google Cloud Run (in progress) — serverless cloud deployment

## Databases & Search
- ChromaDB — local vector store for RAG
- Azure AI Search — enterprise vector search (used at ML Reply)
- Azure Cosmos DB, Azure Table Storage, Azure Data Lake (enterprise projects)
- DuckDB + Parquet (in-progress lakehouse layer)

## Tools & Practices
- uv — Python environment and package management
- pytest — unit and integration testing
- ruff + mypy — linting and static typing
- Semantic Kernel — agent orchestration (enterprise projects)
```

Create at: `services/portfolio-assistant/assets/knowledge-base/skills/tech-stack.md`

- [ ] **Step 5: Create skills/specializations.md**

```markdown
# Mario Avolio — Specialisations

## LLM Orchestration & Agentic Workflows
Designing and implementing multi-step agentic pipelines using LangChain and the
OpenAI Agents SDK. Experience with tool use, planning loops, and agent-to-agent
communication patterns.

## RAG Pipelines & Retrieval Systems
Building retrieval-augmented generation systems with vector stores (Chroma, Azure AI
Search). Covers chunking strategies, embedding selection, retriever tuning, and
lazy pipeline initialisation for zero-cost probe testing.

## Microservices Architecture
Designing self-contained FastAPI microservices with gateway routing, health
aggregation, domain error handling, and YAML-based configuration. Portfolio hub
demonstrates the full pattern end-to-end.

## Model Optimisation
Research background in quantisation, pruning, and self-supervised learning for
efficient model adaptation. Thesis work on facial-attribute classification with
limited labelled data.

## Computer Vision
Image super-resolution (ESRGAN variants), synthetic dataset generation for sonar
imagery, object detection, and declarative reasoning integration for robotic control.
```

Create at: `services/portfolio-assistant/assets/knowledge-base/skills/specializations.md`

- [ ] **Step 6: Create projects/ai-microservices-hub.md**

```markdown
# Project: AI Microservices Hub (Primary Portfolio Project)

## Overview
A production-style microservices hub where a single API gateway fronts a set of
independent generative-AI services. Each service is self-contained with its own
environment, dependencies, tests, and container.

## Architecture
- Gateway (port 8000): service registry, health aggregation, query routing via httpx
- portfolio-assistant (port 5001): RAG chatbot over a local knowledge base (LangChain + ChromaDB)
- text-intelligence (port 5000): structured text analysis (summary, sentiment, tags, language)
- deep-research (port 5002): multi-agent web research producing a markdown report

## Technologies
Python, FastAPI, LangChain, ChromaDB, OpenAI Agents SDK, Docker, Docker Compose,
GitHub Actions, pytest, uv, ruff, mypy

## Key Design Decisions
- Services communicate only through the gateway's routing API; no direct service-to-service calls
- Lazy ML imports: heavy AI stacks load on first query, keeping probes importable at zero cost
- YAML config files per environment; secrets from env only (no .env files committed)
- Probe tests run at zero cost without an API key; functional tests are opt-in
- Gateway degrades gracefully: unreachable services are listed but do not break the hub

## Repository
github.com/MarioAvolio/Portfolio
```

Create at: `services/portfolio-assistant/assets/knowledge-base/projects/ai-microservices-hub.md`

- [ ] **Step 7: Create projects/future-work.md**

```markdown
# Mario Avolio — Work in Progress

The following extensions to the AI Microservices Hub are currently in progress:

## Multi-provider LLM Abstraction Layer
Adding support for Gemini and Azure OpenAI alongside the existing OpenAI provider,
behind a unified interface so services can swap providers via config.

## Cloud Deployment Pipeline
Deploying the hub to Google Cloud Run with expanded GitHub Actions CI/CD, enabling
a live public demo beyond local/Docker Compose.

## Dedicated Agentic Tool-Calling Service
A new microservice exposing a structured tool-calling agent (via OpenAI Agents SDK)
as a gateway-routable query endpoint.

## Lakehouse / Observability Layer
Adding a lightweight lakehouse (S3-compatible storage, Parquet, DuckDB) for logging
queries, tracking costs, and enabling analytics over service usage.
```

Create at: `services/portfolio-assistant/assets/knowledge-base/projects/future-work.md`

- [ ] **Step 8: Create experience/machine-learning-reply.md**

```markdown
# Work Experience: Machine Learning Engineer at Machine Learning Reply

**Company:** Machine Learning Reply
**Role:** Machine Learning Engineer
**Period:** January 2026 – Present
**Location:** Milan, Italy

## Responsibilities
- Building agentic workflows using the OpenAI Agents SDK and Semantic Kernel
- Designing and shipping RAG pipelines with Azure AI Search and Azure OpenAI
- Cloud infrastructure deployment for enterprise generative AI solutions on Azure
- LLM automation at enterprise scale: prompt engineering, evaluation, cost control

## Technologies Used
Azure OpenAI, Azure AI Search, Azure Cosmos DB, Azure Table Storage, Azure Data Lake,
Semantic Kernel, Python, FastAPI, Docker, GitHub Actions
```

Create at: `services/portfolio-assistant/assets/knowledge-base/experience/machine-learning-reply.md`

- [ ] **Step 9: Create experience/research-fellow.md**

```markdown
# Work Experience: Research Fellow at University of Milano-Bicocca

**Institution:** University of Milano-Bicocca — Imaging & Vision Lab
**Role:** Research Fellow
**Period:** January 2025 – December 2025
**Location:** Milan, Italy

## Research Focus
- Synthetic dataset generation for underwater mine detection using side-scan sonar
- Image super-resolution enhancement (ESRGAN-based architectures)
- Underwater target detection and classification

## Achievement
Best Paper Award at ICIAP 2025 (International Conference on Image Analysis and
Processing) for the paper:
"Large-Scale Synthetic Side-Scan Sonar Dataset Generation and Super-Resolution
Enhancement for Underwater Mine Detection" — published by Springer.
```

Create at: `services/portfolio-assistant/assets/knowledge-base/experience/research-fellow.md`

- [ ] **Step 10: Create education/msc-bicocca.md**

```markdown
# Education: MSc in Computer Science — University of Milano-Bicocca

**Degree:** Master of Science in Computer Science
**Institution:** University of Milano-Bicocca
**Period:** September 2021 – March 2024
**Location:** Milan, Italy

## Specialisation
Machine learning, deep learning, computer vision, and model optimisation.

## Thesis
"Self-supervised learning and model adaptation for facial-attribute classification"
Focus: adapting pre-trained vision models to attribute classification with minimal
labelled data, using contrastive and self-supervised pre-training strategies.
```

Create at: `services/portfolio-assistant/assets/knowledge-base/education/msc-bicocca.md`

- [ ] **Step 11: Create education/bsc-calabria.md**

```markdown
# Education: BSc in Computer Science — University of Calabria

**Degree:** Bachelor of Science in Computer Science
**Institution:** University of Calabria (UNICAL)
**Period:** September 2018 – September 2021
**Location:** Cosenza, Italy

## Focus
Algorithms, software engineering, formal methods, and logic programming.

## Thesis
"Computer vision with declarative reasoning for robotic control"
Integrated computer vision outputs with Answer Set Programming (ASP) to enable
a robot agent to reason about and play mobile games from screen captures.
Published as a paper at KR 2023.
```

Create at: `services/portfolio-assistant/assets/knowledge-base/education/bsc-calabria.md`

- [ ] **Step 12: Create publications/iciap-2025.md**

```markdown
# Publication: ICIAP 2025 — Best Paper Award

**Title:** Large-Scale Synthetic Side-Scan Sonar Dataset Generation and
Super-Resolution Enhancement for Underwater Mine Detection

**Conference:** ICIAP 2025 — 23rd International Conference on Image Analysis and Processing
**Publisher:** Springer
**Award:** Best Paper Award
**Year:** 2025

## Summary
The paper addresses the scarcity of labelled sonar data for mine detection by
generating a large-scale synthetic side-scan sonar dataset and combining it with
super-resolution enhancement (ESRGAN-based) to improve downstream detection accuracy.

## Authors
Mario Avolio et al. (Imaging & Vision Lab, University of Milano-Bicocca)
```

Create at: `services/portfolio-assistant/assets/knowledge-base/publications/iciap-2025.md`

- [ ] **Step 13: Create publications/kr-2023.md**

```markdown
# Publication: KR 2023

**Title:** From Vision to Execution: Hybrid Intelligent Robots Playing Mobile Games

**Conference:** KR 2023 — 20th International Conference on Principles of Knowledge
Representation and Reasoning
**Year:** 2023

## Summary
Presents a hybrid intelligent agent that integrates computer vision (object detection
from screen captures) with declarative reasoning via Answer Set Programming (ASP) to
play mobile games autonomously. Demonstrates how neural perception can feed into
symbolic reasoning for robust decision-making in dynamic visual environments.

## Authors
Mario Avolio et al. (University of Calabria)
```

Create at: `services/portfolio-assistant/assets/knowledge-base/publications/kr-2023.md`

- [ ] **Step 14: Verify knowledge base structure**

```powershell
Get-ChildItem -Recurse services/portfolio-assistant/assets/knowledge-base/ | Where-Object { !$_.PSIsContainer } | Select-Object FullName
```

Expected: 12 .md files across 6 folders. No insurance files remaining.

- [ ] **Step 15: Commit knowledge base**

```powershell
git add services/portfolio-assistant/assets/
git commit -m "feat(portfolio-assistant): replace insurance KB with Mario Avolio's portfolio content"
```

---

## Task 9: Final verification

- [ ] **Step 1: Run all service tests**

```powershell
cd services/portfolio-assistant
uv run pytest test/ -v
```

Expected: 5 tests pass (ping, health, status, ready, request_id).

- [ ] **Step 2: Run gateway tests**

```powershell
cd ../../gateway
uv run pytest test/ -v
```

Expected: all gateway tests pass.

- [ ] **Step 3: Verify no stale insurellm references in source**

```powershell
cd ..
Select-String -Recurse -Include "*.py","*.yml","*.yaml","*.toml","*.md" `
  -Pattern "insurellm" `
  -Path "gateway","services/portfolio-assistant","docker-compose.yml","docs/ARCHITECTURE.md" |
  Where-Object { $_.Path -notmatch "vector_db|\.venv" }
```

Expected: zero matches.

- [ ] **Step 4: Final commit if any cleanup needed**

```powershell
git add -A
git commit -m "chore(portfolio-assistant): clean up stale insurellm references"
```

---

## Self-review

**Spec coverage:**
- [x] Directory rename with git history preserved (Task 1)
- [x] All config identifiers updated (Task 2)
- [x] System prompt reflects Mario's domain (Task 3)
- [x] All docstrings updated (Task 4)
- [x] Tests updated and verified (Task 5)
- [x] Gateway registry updated (Task 6)
- [x] docker-compose env var updated (Task 7)
- [x] ARCHITECTURE.md updated (Task 7)
- [x] Old KB deleted + vector_db cleared (Task 8, Step 1)
- [x] 12 new KB files with real data (Task 8, Steps 2-13)
- [x] Final grep for stale refs (Task 9, Step 3)

**Type consistency:** No new types introduced. All modified code uses existing types unchanged.

**Placeholder scan:** No TBD/TODO/placeholder content. All KB files contain real content from marioavolio.netlify.app.
