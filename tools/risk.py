from typing import Optional

from langchain_core.tools import tool
from app.ml import open_ticket_predictions


@tool
def get_escalation_risk(ticket_id: Optional[str] = None) -> dict:
    """Retrieve ML-based escalation risk for a specific ticket or all predicted tickets.

Use a ticket ID such as TKT-009 when checking one ticket.
Do not pass a customer ID such as CUSTOMER-001 to this tool.
To find a customer's tickets first, use get_open_tickets."""

    if ticket_id is None:
        return {
            "predictions": [
                {
                    "ticket_id": ticket_id,
                    "customer_id": prediction["customer_id"],
                    "escalation_probability": prediction["escalation_probability"],
                    "risk_level": prediction["risk_level"],
                }
                for ticket_id, prediction in open_ticket_predictions.items()
            ]
        }

    prediction = open_ticket_predictions.get(ticket_id)

    if prediction is None:
        return {
            "ticket_id": ticket_id,
            "message": f"No escalation prediction found for ticket {ticket_id}"
        }

    return {
        "ticket_id": ticket_id,
        "customer_id": prediction["customer_id"],
        "escalation_probability": prediction["escalation_probability"],
        "risk_level": prediction["risk_level"],
    }


if __name__ == "__main__":
    result = get_escalation_risk.invoke({"ticket_id": "TKT-009"})
    print(result)
