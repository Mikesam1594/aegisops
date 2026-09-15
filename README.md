# AegisOps — AI Incident Intelligence Copilot

> **On-Premises First • Cloud Ready • Deployment Flexible**

An enterprise AI incident investigation copilot designed for
**on-premises deployment and adaptable to cloud environments based on
customer requirements**.

AegisOps combines **Agentic AI, Retrieval-Augmented Generation (RAG),
machine learning, structured business tools, and LLM inference** to
investigate incidents, assess escalation risk, analyze customer
vulnerability, and retrieve historical troubleshooting knowledge.

---

## Overview

Enterprise support and incident teams often need to correlate information
across customer history, open tickets, historical incidents,
knowledge-base articles, predictive risk signals, and vulnerability
assessments before deciding what to investigate or escalate.

**AegisOps** brings these capabilities together through a
LangChain-based tool-using AI agent.

Instead of following a fixed workflow, the agent dynamically determines
which tools are relevant to the user's question, gathers information from
multiple sources, correlates the results, and produces an
evidence-grounded investigation response.

The architecture is designed to support **different enterprise deployment
requirements**, with an on-premises-first implementation and the ability
to adapt infrastructure and LLM providers for cloud deployments.

---

## Why AegisOps?

AegisOps demonstrates how enterprise AI can move beyond a simple chatbot
or standalone RAG application.

It combines:

- 🤖 **Agentic AI** — dynamic tool selection and orchestration
- 🔎 **RAG** — retrieval of technical knowledge and historical incidents
- 🧠 **ML Risk Prediction** — escalation likelihood for open tickets
- 👤 **Customer Intelligence** — historical support profiles
- ⚠️ **Vulnerability Assessment** — customer-level risk assessment
- 🔗 **Multi-Tool Reasoning** — correlation across structured and
  unstructured information
- 🛡️ **Grounded Responses** — separation of evidence, inference, and
  recommended investigation
- 🏠 **On-Premises AI** — local LLM and data processing
- ☁️ **Cloud Adaptability** — architecture can be adapted to cloud
  infrastructure when required
- 🚀 **FastAPI** — API layer for enterprise integration

---

## Deployment Philosophy

### On-Premises First. Cloud Ready.

AegisOps is designed around a **deployment-flexible architecture**.

The current implementation demonstrates an on-premises-oriented deployment
where LLM inference, embeddings, vector search, ML processing, and
application execution can remain within the customer environment.

For customers that prefer cloud infrastructure, individual infrastructure
components can be substituted with managed or cloud-based services while
preserving the core agent, tools, business logic, and investigation
workflow.

### On-Premises Deployment

Suitable for environments with requirements around:

- Data residency
- Data privacy
- Security
- Network isolation
- Customer-controlled infrastructure
- Local AI inference

```text
┌──────────────────────────────────────────────┐
│           Customer Environment                │
│                                              │
│  Support Data ──┐                            │
│  Ticket Data ───┼──► FastAPI                 │
│  KB Data ───────┘        │                   │
│                          ▼                   │
│                    AI Agent                  │
│                          │                   │
│          ┌───────────────┼──────────────┐    │
│          ▼               ▼              ▼    │
│     Customer Tools   ML Risk          RAG    │
│                          │              │    │
│                          │           Qdrant  │
│                          │              │    │
│          └───────────────┼──────────────┘    │
│                          ▼                   │
│                    Local LLM                │
│                    Qwen3 + Ollama            │
│                          │                   │
│                          ▼                   │
│                  AI Investigation            │
│                     Response                 │
└──────────────────────────────────────────────┘
```

### Cloud Deployment

For customers that prefer managed infrastructure, the same core
architecture can be adapted to use:

- Cloud-based LLM providers
- Managed vector databases
- Cloud-hosted APIs
- Enterprise cloud data stores
- Managed observability infrastructure

```text
┌──────────────────────────────────────────────┐
│              Cloud Environment               │
│                                              │
│       Enterprise Data / Systems              │
│                    │                         │
│                    ▼                         │
│                 FastAPI                      │
│                    │                         │
│                    ▼                         │
│                AI Agent                      │
│                    │                         │
│        ┌───────────┼────────────┐            │
│        ▼           ▼            ▼            │
│     Tools       ML Engine    Vector DB       │
│                                  │           │
│                                  ▼           │
│                              Cloud LLM       │
│                                  │           │
│                                  ▼           │
│                         AI Investigation     │
└──────────────────────────────────────────────┘
```

### Deployment Principle

The goal is to keep the **agent orchestration, business tools, ML
workflow, and API layer independent of the underlying deployment model**.

This allows the solution to be adapted according to customer requirements
rather than forcing every customer into a single architecture.

> **On-premises when data must remain within the customer environment.
> Cloud when the customer prefers managed infrastructure.**

---

## Architecture

```text
                         AegisOps
              AI Incident Intelligence
                         │
                         ▼
                  ┌───────────────┐
                  │    FastAPI    │
                  └───────┬───────┘
                          │
                          ▼
                ┌───────────────────┐
                │   LangChain       │
                │   AI Agent        │
                │   Qwen3 8B        │
                └─────────┬─────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
   Customer Tools     ML Risk Engine      RAG
          │               │                │
          ▼               ▼                ▼
   Customer Profile   Scikit-learn      Qdrant
   Open Tickets       Escalation Risk       │
   Vulnerability                           ├── KB Articles
                                           └── Resolved Incidents
                          │
                          ▼
                  Grounded AI Response
```

---

## Agentic Tool Orchestration

AegisOps uses a LangChain-based tool-using agent with five specialized
tools.

### Available Tools

| Tool | Purpose |
|---|---|
| `get_customer_profile` | Retrieves customer support history and profile |
| `get_open_tickets` | Retrieves current open tickets |
| `get_escalation_risk` | Retrieves ML-based escalation prediction for a ticket |
| `get_vulnerability` | Retrieves customer vulnerability assessment |
| `search_knowledge_base` | Searches KB articles and resolved historical incidents |

The LLM determines which tools are relevant to the user's question and can
combine results from multiple tools.

For example:

```text
User Question
      │
      ▼
   AI Agent
      │
      ├── Customer Profile
      │
      ├── Open Tickets
      │
      ├── Escalation Risk
      │
      ├── Vulnerability
      │
      └── Knowledge Base
              │
              ▼
       Correlate Results
              │
              ▼
      Grounded Response
```

The workflow is **agent-driven rather than a hardcoded execution sequence**.

---

## RAG — Retrieval-Augmented Generation

The RAG pipeline provides access to technical knowledge and historical
incident information.

### RAG Components

- **Sentence Transformers** for embeddings
- **Qdrant** for vector search
- Knowledge-base articles
- Resolved historical support tickets
- **Ollama** for local LLM generation

KB articles are split into smaller chunks before indexing.

Resolved historical tickets are embedded as complete incidents to enable
semantic retrieval of similar previously resolved problems.

Qdrant uses local persistent storage so the demo corpus does not need to
be re-indexed on every application startup.

### Example

```text
An authentication failure started after an SSL certificate change.
What should I investigate and what similar incidents have been resolved?
```

The knowledge-base tool retrieves relevant technical articles and
historical incidents before the agent generates its investigation response.

---

## ML-Based Escalation Risk

AegisOps includes a machine-learning pipeline for predicting the likelihood
that an open support ticket will escalate.

Historical resolved tickets are used to train a
**Scikit-learn Logistic Regression** model.

### Features

The model uses information such as:

- Historical ticket count
- Previous escalation count
- Historical escalation rate
- Average previous resolution time
- Ticket priority
- Ticket impact
- Recent-change information

The model produces an escalation probability for open tickets and maps the
probability to a risk level.

### Example

```text
Ticket: TKT-009

Escalation probability: 97.57%
Risk level: high
```

The project uses a **70% probability threshold** for open-ticket risk
classification.

> **Important:** The dataset is synthetic and intentionally small. The ML
> evaluation demonstrates the engineering pipeline and should not be treated
> as evidence of production model performance.

---

## Customer Intelligence

AegisOps builds historical customer profiles from resolved support tickets.

Customer profiles provide structured information that can be used by the
agent during incident investigation.

The profile can include:

- Historical ticket volume
- Historical escalation rate
- Average resolution time
- Customer vulnerability score
- Customer vulnerability level

This allows the agent to investigate incidents in the context of the
customer's historical support behavior.

---

## Customer Vulnerability Assessment

Customer vulnerability is calculated using a rule-based assessment based on:

- Historical escalation rate
- Average historical resolution time

The resulting vulnerability assessment is stored in the customer profile
and exposed through a dedicated tool.

This keeps the vulnerability logic separate from the LLM and makes the
result deterministic and inspectable.

---

## Grounded AI Responses

AegisOps is designed to distinguish between:

### Confirmed Facts

Information directly returned by the available tools.

### Evidence-Based Inferences

Reasonable conclusions supported by retrieved data.

### Investigation Recommendations

Suggested next steps that should be verified by an engineer.

Retrieved historical incidents and KB matches are treated as **evidence**,
not automatic confirmation of the current incident's root cause.

This helps reduce the risk of presenting a similar historical incident as
the definitive explanation for a new incident.

---

## Example Questions

### Customer Intelligence

```text
What is the vulnerability level of CUSTOMER-001?
```

```text
Show me CUSTOMER-001's profile and open tickets.
```

### Risk Investigation

```text
Which of CUSTOMER-001's open tickets are most likely to escalate?
```

```text
What is the escalation risk of TKT-009?
```

### Incident Investigation

```text
An authentication failure started after an SSL certificate change.
What should I investigate and what similar incidents have been resolved?
```

### Cross-Tool Investigation

```text
Which open tickets for CUSTOMER-001 have the highest escalation risk?
```

The agent can retrieve the customer's open tickets first and then query the
ML risk tool for the relevant tickets.

---

## Project Structure

```text
AegisOps/
├── app/
│   ├── agent.py
│   ├── customer_profile.py
│   ├── ingestion.py
│   ├── main.py
│   ├── ml.py
│   ├── models.py
│   ├── ollama_client.py
│   └── rag.py
│
├── tools/
│   ├── __init__.py
│   ├── customer.py
│   ├── knowledge.py
│   ├── risk.py
│   ├── tickets.py
│   └── vulnerability.py
│
├── data/
│   └── ingestion/
│       └── demo/
│           ├── kb_articles.json
│           └── support_tickets.json
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Application and ML development |
| **FastAPI** | REST API |
| **LangChain** | Agent and tool orchestration |
| **Qwen3 8B** | Local LLM |
| **Ollama** | Local LLM runtime |
| **Qdrant** | Vector database |
| **Sentence Transformers** | Text embeddings |
| **Scikit-learn** | Escalation-risk prediction |

---

## Prerequisites

- Python 3.11+
- Ollama
- Qwen3 8B

Pull the model:

```bash
ollama pull qwen3:8b
```

---

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd AegisOps
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Swagger UI can be used to interactively test the `/ask` endpoint.

### Example Request

`POST /ask`

```json
{
  "query": "Which of CUSTOMER-001's open tickets are most likely to escalate?"
}
```

---

## Design Decisions

### 1. Agent-Driven Tool Selection

The project does not hardcode a fixed execution sequence.

The LLM determines which tools are relevant to the user's question and
can combine results from multiple tools.

### 2. Structured Data vs. Unstructured Knowledge

Structured operational information such as:

- Customer profiles
- Open tickets
- Escalation predictions
- Vulnerability assessments

is exposed through dedicated tools.

Technical knowledge and historical incidents are handled through semantic
retrieval.

### 3. Separate ML Prediction from LLM Reasoning

The escalation probability comes from the Scikit-learn model.

The LLM consumes the returned prediction when explaining, comparing, or
prioritizing ticket risk.

The LLM does not independently invent an escalation probability.

### 4. Evidence Before Conclusions

Retrieved historical incidents and KB articles are treated as supporting
evidence.

The agent is instructed not to automatically treat similarity as proof of
the current incident's root cause.

### 5. Deployment Flexibility

The application separates the agent, business tools, ML workflow, and API
layer from the underlying deployment infrastructure.

This allows the solution to support an **on-premises-first deployment**
while remaining adaptable to cloud infrastructure when customer
requirements change.

---

## Limitations

- The support dataset is synthetic.
- The ML dataset is small and is not production training data.
- Vulnerability assessment is rule-based.
- Qdrant uses local persistent storage.
- Authentication and authorization are not implemented.
- Production deployment configuration is not included.
- The project uses a single agent.
- The project uses LangChain agent orchestration rather than a custom
  LangGraph workflow.
- Model and agent evaluation are limited to the portfolio/demo scope.

---

## Future Enhancements

Potential production-oriented enhancements include:

- MCP-based enterprise integrations
- ITSM and ticketing-system connectors
- Human-in-the-loop remediation approval
- Agent evaluation and regression testing
- Observability and tracing
- Authentication and authorization
- Production vector database deployment
- Larger anonymized training datasets
- Frontend investigation dashboard
- Docker-based deployment
- Production deployment configuration
- Pluggable LLM providers
- Cloud deployment profiles

---

## Portfolio Focus

AegisOps was built to demonstrate practical AI engineering across the
complete workflow:

```text
                    Enterprise Data
                          │
                          ▼
                      Ingestion
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
        ML Risk Prediction       RAG / Search
              │                       │
              └───────────┬───────────┘
                          ▼
                  Agentic AI Agent
                          │
                          ▼
                   Tool Orchestration
                          │
                          ▼
                    LLM Reasoning
                          │
                          ▼
                 Grounded Investigation
                          │
                          ▼
                       FastAPI
```

The project focuses on the intersection of:

**AI Engineering + Agentic AI + RAG + Machine Learning +
Enterprise Integration + On-Premises AI + Cloud Adaptability**

---

## Key Takeaway

AegisOps demonstrates an enterprise AI architecture where the deployment
model can be selected according to customer requirements.

**On-premises when data control and local inference are priorities.**

**Cloud when managed infrastructure and cloud-based services are preferred.**

The core investigation workflow remains centered around the same agent,
tools, business logic, ML pipeline, and API layer.

---

## Disclaimer

This is a synthetic portfolio project created to demonstrate AI engineering
and enterprise AI architecture concepts.

The included support tickets and knowledge-base articles are demo data and
should not be treated as real customer information.
