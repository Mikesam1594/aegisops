from typing import Optional

from langchain_core.tools import tool
from app.ingestion import normalized_tickets


@tool
def get_open_tickets(customer_id: Optional[str] = None) -> dict:
    """Retrieve open support tickets for a customer or all customers."""

    open_tickets = [
        ticket
        for ticket in normalized_tickets
        if ticket.status == "open"
        and (customer_id is None or ticket.customer_id == customer_id)
    ]

    tickets = []

    for ticket in open_tickets:
        tickets.append({
            "ticket_id": ticket.ticket_id,
            "customer_id": ticket.customer_id,
            "title": ticket.title,
            "description": ticket.description,
            "priority": ticket.priority,
            "impact": ticket.impact,
            "category": ticket.category,
            "environment": ticket.environment,
            "recent_change": ticket.recent_change,
        })

    return {
        "customer_id": customer_id,
        "open_tickets": tickets,
    }


if __name__ == "__main__":
    result = get_open_tickets.invoke({"customer_id": "CUSTOMER-001"})
    print(result)
