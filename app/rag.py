import json
import re

from app.ingestion import normalized_tickets
from app.ollama_client import ask_ollama
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer


# ============================================================
# 1. INITIALIZATION / SHARED RESOURCES
# ============================================================
# FastAPI later:
# These objects should be created once when the application starts,
# not recreated for every API request.
qdrant = QdrantClient(path="data/qdrant")
model = SentenceTransformer("all-MiniLM-L6-v2")


# ============================================================
# 2. LOAD DEMO KNOWLEDGE BASE DATA
# ============================================================
# Learning/demo source only.
# In a real deployment, ingestion would retrieve KB data from
# the customer source system or another configured repository.
with open("data/ingestion/demo/kb_articles.json", "r") as file:
    kb_articles = json.load(file)


# ============================================================
# 3. CHUNK KNOWLEDGE BASE ARTICLES
# ============================================================
def chunk_article(article, chunk_size=300):
    """Split one KB article into sentence-aware chunks."""

    content = article["content"]

    # Split only after '.', '!' or '?' followed by whitespace so that
    # we avoid cutting words/sentences in the middle.
    sentences = re.split(r'(?<=[.!?])\s+', content)

    # Stores completed chunks.
    chunks = []

    # Temporary chunk currently being built.
    current_chunk = ""

    for sentence in sentences:
        # Check whether the new sentence still fits in the current chunk.
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            if current_chunk:
                # Add a space before subsequent sentences.
                current_chunk += " " + sentence
            else:
                # First sentence in the current chunk.
                current_chunk = sentence

        else:
            # Current chunk is full, so store it before starting a new one.
            chunks.append(
                {
                    "article_id": article["article_id"],
                    "title": article["title"],
                    "category": article["category"],
                    "text": current_chunk,
                }
            )

            # Start the next chunk with the sentence that did not fit.
            current_chunk = sentence

    # Store the final chunk if there is anything left.
    if current_chunk:
        chunks.append(
            {
                "article_id": article["article_id"],
                "title": article["title"],
                "category": article["category"],
                "text": current_chunk,
            }
        )

    return chunks


# Create the complete list of KB chunks.
all_chunks = []

for article in kb_articles:
    article_chunks = chunk_article(article)
    all_chunks.extend(article_chunks)

print("Total chunks:", len(all_chunks))
# Learning checkpoint:
# print("First chunk:", all_chunks[0])


# ============================================================
# 4-7. INDEX KB CHUNKS INTO QDRANT
# ============================================================
# Qdrant is persistent, so only build embeddings and store them
# when the collection does not already exist.
if not qdrant.collection_exists("kb_articles"):

    # ========================================================
    # 4. EMBED KB CHUNKS
    # ========================================================
    embedded_chunks = []

    for chunk in all_chunks:
        # Convert chunk text into a 384-dimensional semantic vector.
        embedding = model.encode(chunk["text"])

        embedded_chunks.append(
            {
                "chunk": chunk,
                "embedding": embedding,
            }
        )

    # Learning checkpoint:
    # print("Embedded chunks:", len(embedded_chunks))
    # print("Embedding dimensions:", len(embedded_chunks[0]["embedding"]))

    # ========================================================
    # 5. CREATE KB QDRANT COLLECTION
    # ========================================================
    # All KB embeddings use all-MiniLM-L6-v2, which produces 384 dimensions.
    qdrant.create_collection(
        collection_name="kb_articles",
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
    )

    # ========================================================
    # 6. CREATE KB QDRANT POINTS
    # ========================================================
    points = []

    for index, embedded_chunk in enumerate(embedded_chunks):
        points.append(
            PointStruct(
                # Qdrant point ID uniquely identifies this vector record.
                id=index + 1,
                vector=embedded_chunk["embedding"].tolist(),
                # Payload keeps the source metadata and text alongside the vector.
                payload=embedded_chunk["chunk"],
            )
        )

    print("Qdrant points:", len(points))

    # ========================================================
    # 7. STORE KB POINTS IN QDRANT
    # ========================================================
    qdrant.upsert(
        collection_name="kb_articles",
        points=points,
    )

    print("KB points stored:", qdrant.count(collection_name="kb_articles"))

else:
    print("KB collection already exists. Reusing persisted embeddings.")


# ============================================================
# 8. PREPARE RESOLVED HISTORICAL TICKETS
# ============================================================
# ============================================================
# We consume canonical SupportTicket objects produced by ingestion.py.
# Resolved tickets become our second retrieval source.
resolved_tickets = [
    ticket
    for ticket in normalized_tickets
    if ticket.status == "resolved"
]

# Learning checkpoint:
# print("Resolved tickets:", len(resolved_tickets))


ticket_documents = []

for ticket in resolved_tickets:
    # One resolved ticket is treated as one searchable semantic document
    # in v1 because these synthetic tickets are relatively short.
    ticket_text = f"""
Title: {ticket.title}
Description: {ticket.description}
Error: {ticket.error_message or ""}
Technician Investigation: {ticket.technician_investigation or ""}
Resolution: {ticket.resolution or ""}
Resolution Summary: {ticket.resolution_summary or ""}
Outcome: {ticket.outcome or ""}
"""

    ticket_documents.append(
        {
            "ticket_id": ticket.ticket_id,
            "customer_id": ticket.customer_id,
            "text": ticket_text,
        }
    )


# ============================================================
# 9-12. INDEX RESOLVED TICKETS INTO QDRANT
# ============================================================
# Resolved tickets are persisted in Qdrant as one vector per ticket.
# Only generate embeddings and store them when the collection does not
# already exist.
if not qdrant.collection_exists("resolved_tickets"):

    # ========================================================
    # 9. EMBED RESOLVED TICKETS
    # ========================================================
    ticket_embeddings = []

    for document in ticket_documents:
        embedding = model.encode(document["text"])

        ticket_embeddings.append(
            {
                "ticket_id": document["ticket_id"],
                "customer_id": document["customer_id"],
                "text": document["text"],
                "embedding": embedding,
            }
        )

    # Learning checkpoints:
    # print("Ticket embeddings:", len(ticket_embeddings))
    # print("First ticket:", ticket_embeddings[0]["ticket_id"])
    # print("Embedding dimensions:", len(ticket_embeddings[0]["embedding"]))

    # ========================================================
    # 10. CREATE RESOLVED TICKET QDRANT COLLECTION
    # ========================================================
    qdrant.create_collection(
        collection_name="resolved_tickets",
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
    )

    # ========================================================
    # 11. CREATE RESOLVED TICKET QDRANT POINTS
    # ========================================================
    ticket_points = []

    for index, ticket_embedding in enumerate(ticket_embeddings):
        ticket_points.append(
            PointStruct(
                id=index + 1,
                vector=ticket_embedding["embedding"].tolist(),
                payload={
                    "ticket_id": ticket_embedding["ticket_id"],
                    "customer_id": ticket_embedding["customer_id"],
                    "text": ticket_embedding["text"],
                },
            )
        )

    print("Ticket Qdrant points:", len(ticket_points))

    # ========================================================
    # 12. STORE RESOLVED TICKETS IN QDRANT
    # ========================================================
    qdrant.upsert(
        collection_name="resolved_tickets",
        points=ticket_points,
    )

    print(
        "Resolved ticket points stored:",
        qdrant.count(collection_name="resolved_tickets"),
    )

else:
    print(
        "Resolved ticket collection already exists. "
        "Reusing persisted embeddings."
    )


# ============================================================
# 13. RUN RAG FOR ONE USER QUERY
# ============================================================
# ============================================================
# FastAPI later:
# The hardcoded query is removed. FastAPI will call run_rag(request.query).
def run_rag(query_text):
    """Retrieve evidence, call the LLM, and return a structured RAG response."""

    # --------------------------------------------------------
    # 13.1 EMBED CURRENT INCIDENT
    # --------------------------------------------------------
    # Convert the user's query into the same 384-dimensional
    # vector space as the indexed KB and ticket data.
    query_embedding = model.encode(query_text)

    # Learning checkpoint:
    # print("Query embedding dimensions:", len(query_embedding))

    # --------------------------------------------------------
    # 13.2 RETRIEVE RELEVANT KB CHUNKS
    # --------------------------------------------------------
    search_results = qdrant.query_points(
        collection_name="kb_articles",
        query=query_embedding.tolist(),
        limit=5,
    )

    # --------------------------------------------------------
    # 13.3 AGGREGATE CHUNK SCORES BY ARTICLE
    # --------------------------------------------------------
    # Several chunks can belong to the same article.
    # We combine those scores to get an article-level relevance signal.
    article_scores = {}

    for result in search_results.points:
        article_id = result.payload["article_id"]
        score = result.score

        if article_id not in article_scores:
            article_scores[article_id] = 0

        article_scores[article_id] += score

    # Learning checkpoints:
    # print("Article scores:")
    # for article_id, score in article_scores.items():
    #     print(article_id, score)

    # --------------------------------------------------------
    # 13.4 RANK ARTICLES
    # --------------------------------------------------------
    ranked_articles = sorted(
        article_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    # --------------------------------------------------------
    # 13.5 FETCH COMPLETE ORIGINAL ARTICLES
    # --------------------------------------------------------
    # Qdrant identified the relevant article IDs through chunks.
    # We now return the complete original articles as LLM context.
    relevant_articles = []

    for article_id, _score in ranked_articles:
        for article in kb_articles:
            if article["article_id"] == article_id:
                relevant_articles.append(article)
                break

    # Final KB context is limited to the top 2 articles for v1.
    top_articles = relevant_articles[:2]

    # Authoritative IDs come from Python, not from the LLM.
    kb_ids = [article["article_id"] for article in top_articles]

    # --------------------------------------------------------
    # 13.6 RETRIEVE SIMILAR RESOLVED INCIDENTS
    # --------------------------------------------------------
    ticket_search_results = qdrant.query_points(
        collection_name="resolved_tickets",
        query=query_embedding.tolist(),
        limit=3,
    )

    top_tickets = ticket_search_results.points[:3]

    # Authoritative ticket IDs also come directly from Qdrant payloads.
    ticket_ids = [
        result.payload["ticket_id"]
        for result in top_tickets
    ]

    # Learning checkpoint:
    # for result in top_tickets:
    #     print("Ticket ID:", result.payload["ticket_id"])
    #     print("Score:", result.score)
    #     print(result.payload["text"])
    #     print()

    # --------------------------------------------------------
    # 13.7 BUILD GROUNDED CONTEXT
    # --------------------------------------------------------
    rag_context = "RELEVANT KNOWLEDGE BASE:\n\n"

    for article in top_articles:
        rag_context += f"""
Article ID: {article["article_id"]}
Title: {article["title"]}
Category: {article["category"]}
Content:
{article["content"]}

"""

    rag_context += "\nSIMILAR RESOLVED INCIDENTS:\n\n"

    for result in top_tickets:
        rag_context += f"""
Ticket ID: {result.payload["ticket_id"]}
Customer ID: {result.payload["customer_id"]}
Similarity Score: {result.score}
Incident Evidence:
{result.payload["text"]}

"""

    # --------------------------------------------------------
    # 13.8 BUILD GROUNDED LLM PROMPT
    # --------------------------------------------------------
    prompt = f"""
You are an enterprise support copilot.

Analyze the current incident using the provided evidence.

CURRENT INCIDENT:
{query_text}

{rag_context}

INSTRUCTIONS:
- Recommend the most likely troubleshooting or resolution steps.
- Prefer the knowledge base guidance and successful historical resolutions.
- Do not invent facts that are not supported by the evidence.
- Clearly distinguish between evidence and your own inference.
- If the evidence is insufficient, say so.
- Treat historical resolved incidents as reference evidence, not guaranteed truth.
- Do not invent source IDs.
"""

    # --------------------------------------------------------
    # 13.9 CALL LOCAL LLM
    # --------------------------------------------------------
    llm_response = ask_ollama(prompt)

    # --------------------------------------------------------
    # 13.10 BUILD STRUCTURED RESPONSE
    # --------------------------------------------------------
    # FastAPI can return this dictionary directly as JSON.
    # Source IDs are authoritative because Python generated them from
    # the retrieval results rather than relying on the LLM to reproduce them.
    final_response = {
        "query": query_text,
        "recommendation": llm_response,
        "supporting_kb_articles": kb_ids,
        "supporting_resolved_tickets": ticket_ids,
    }

    return final_response


# ============================================================
# 14. LOCAL TEST ENTRY POINT
# ============================================================
# FastAPI later:
# This block is only for local testing. It will not run when another
# module imports run_rag().
if __name__ == "__main__":
    test_query = "The API authentication is failing because the access token may have expired."

    result = run_rag(test_query)
    print(result)
