# AI Support & Incident Copilot

An AI-powered support and incident investigation copilot combining
agentic tool calling, RAG, machine learning, and FastAPI to investigate
support tickets, assess escalation risk, understand customer
vulnerability, and retrieve troubleshooting knowledge.

## Overview

Support engineers often need to correlate customer history, open
tickets, historical incidents, knowledge-base articles, ML predictions,
and vulnerability assessments. This project brings those capabilities
together through a LangChain-based tool-using agent.

The agent dynamically selects the tools relevant to each question rather
than following a hardcoded workflow.

## Architecture

``` text
User
  |
  v
FastAPI
  |
  v
LangChain Agent (Qwen3 8B)
  |
  +--> Customer Profile Tool
  +--> Open Tickets Tool
  +--> Escalation Risk Tool --> Scikit-learn
  +--> Vulnerability Tool
  +--> Knowledge Base Tool --> Qdrant
                              |
                              +--> KB Articles
                              +--> Resolved Tickets
  |
  v
Final Answer
```

## Key Capabilities

### Agentic Tool Orchestration

The agent uses five tools:

-   `get_customer_profile` --- customer support history and profile.
-   `get_open_tickets` --- current open tickets.
-   `get_escalation_risk` --- ML-based escalation prediction for a
    ticket.
-   `get_vulnerability` --- customer vulnerability assessment.
-   `search_knowledge_base` --- semantic search over KB articles and
    resolved incidents.

The LLM chooses which tools to call and can combine results from
multiple tools.

### RAG

The RAG pipeline uses:

-   Sentence Transformers for embeddings
-   Qdrant for vector search
-   Knowledge-base articles
-   Resolved historical support tickets
-   Ollama for local LLM generation

KB articles are chunked before indexing. Resolved tickets are embedded
as complete incidents. Qdrant collections use local persistent storage
so the demo corpus is not re-indexed on every startup.

### ML Escalation Risk

Historical resolved tickets are used to train a Logistic Regression
model.

Features include historical ticket count, previous escalations,
historical escalation rate, previous average resolution time, priority,
impact, and recent-change information.

The model produces an escalation probability for open tickets and maps
it to a risk level.

Example:

``` text
TKT-009
Escalation probability: 97.57%
Risk level: high
```

The project uses a 70% probability threshold for open-ticket
predictions.

> The dataset is synthetic and small. The ML evaluation demonstrates the
> pipeline and should not be treated as evidence of production model
> performance.

### Customer Vulnerability

Customer vulnerability is calculated using a rule-based assessment based
on historical escalation rate and average historical resolution time.

The result is stored in the customer profile and exposed through a
dedicated tool.

### Grounded Responses

The agent is instructed to distinguish between confirmed facts,
evidence-based inferences, and recommended investigation steps.

Retrieved historical incidents and KB matches are treated as evidence
rather than automatic confirmation of a current incident's root cause.

## Example Questions

``` text
What is the vulnerability level of CUSTOMER-001?
```

``` text
Show me CUSTOMER-001's profile and open tickets.
```

``` text
Which of CUSTOMER-001's open tickets are most likely to escalate?
```

``` text
An authentication failure started after an SSL certificate change.
What should I investigate and what similar incidents have been resolved before?
```

``` text
What is the escalation risk of TKT-009?
```

## Project Structure

``` text
Ai-Support-CoPilot/
├── app/
│   ├── agent.py
│   ├── customer_profile.py
│   ├── ingestion.py
│   ├── main.py
│   ├── ml.py
│   ├── models.py
│   ├── ollama_client.py
│   └── rag.py
├── tools/
│   ├── __init__.py
│   ├── customer.py
│   ├── knowledge.py
│   ├── risk.py
│   ├── tickets.py
│   └── vulnerability.py
├── data/
│   └── ingestion/
│       └── demo/
│           ├── kb_articles.json
│           └── support_tickets.json
├── requirements.txt
├── .gitignore
└── README.md
```

## Technology Stack

  Technology              Purpose
  ----------------------- --------------------------------
  Python                  Application and ML development
  FastAPI                 REST API
  LangChain               Agent and tool orchestration
  Qwen3 8B                Local LLM
  Ollama                  Local LLM runtime
  Qdrant                  Vector database
  Sentence Transformers   Embeddings
  Scikit-learn            Escalation-risk model

## Prerequisites

-   Python 3.11+
-   Ollama
-   Qwen3 8B

Pull the model:

``` bash
ollama pull qwen3:8b
```

## Installation

``` bash
git clone <your-repository-url>
cd Ai-Support-CoPilot
```

### macOS / Linux

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

``` powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

## Running the Application

``` bash
uvicorn app.main:app --reload
```

The API runs at:

``` text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

``` text
http://127.0.0.1:8000/docs
```

Example request to `POST /ask`:

``` json
{
  "query": "Which of CUSTOMER-001's open tickets are most likely to escalate?"
}
```

## Design Decisions

### Agent-driven tool selection

The project does not hardcode a fixed execution sequence. The LLM
determines which tools are relevant to the user's question.

### Structured data vs. unstructured knowledge

Customer profiles, open tickets, risk predictions, and vulnerability
assessments remain structured data exposed through tools. Technical
knowledge and historical incidents are handled through semantic
retrieval.

### Separate ML prediction from LLM reasoning

The escalation probability comes from the scikit-learn model. The LLM
consumes the returned prediction when explaining and comparing ticket
risk.

### Local / on-premises orientation

The LLM runs locally through Ollama, demonstrating an architecture where
support data and inference can remain within a customer environment.

## Limitations

-   The support dataset is synthetic.
-   The ML dataset is small and is not production training data.
-   Vulnerability assessment is rule-based.
-   Qdrant uses local persistent storage.
-   Authentication and authorization are not implemented.
-   Production deployment configuration is not included.
-   The project uses a single agent.
-   The project uses LangChain agent orchestration rather than a custom
    LangGraph workflow.

## Future Enhancements

-   MCP-based enterprise integrations
-   ITSM/ticketing connectors
-   Human-in-the-loop remediation approval
-   Agent evaluation and regression testing
-   Observability and tracing
-   Authentication and authorization
-   Production vector database deployment
-   Larger anonymized training datasets
-   Frontend dashboard
-   Docker and production deployment

## Disclaimer

This is a synthetic portfolio project for demonstrating AI engineering
concepts. The included support tickets and knowledge-base articles are
demo data and should not be treated as real customer information.
