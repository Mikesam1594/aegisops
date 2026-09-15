from langchain_core.tools import tool
from app.rag import run_rag


@tool
def search_knowledge_base(query: str) -> dict:
    """Search KB articles and resolved historical incidents for
    troubleshooting, root-cause analysis, resolution guidance, or
    similar historical incidents.

    Use this tool for unstructured technical knowledge. Do not use it
    for customer profiles, open-ticket lists, escalation risk, or
    vulnerability assessments, which are provided by dedicated tools."""

    result = run_rag(query)

    return result


if __name__ == "__main__":
    result = search_knowledge_base.invoke({
        "query": "authentication failure after SSL certificate change"
    })

    print(result)
