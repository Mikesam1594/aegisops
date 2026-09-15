import json

from app.models import SupportTicket


def normalize_ticket(data):
    return SupportTicket(
        ticket_id=data["ticket_id"],
        customer_id=data.get("customer_id"),
        source=data["source"],
        product=data.get("product"),
        title=data["title"],
        description=data["description"],
        error_message=data.get("error_message"),
        environment=data["environment"],
        recent_change=data.get("recent_change"),
        impact=data["impact"],
        category=data.get("category"),
        priority=data["priority"],
        status=data["status"],
        created_at=data["created_at"],
        resolved_at=data.get("resolved_at"),
        resolution_time_hours=data.get("resolution_time_hours"),
        escalated=data.get("escalated"),
        technician_investigation=data.get("technician_investigation"),
        resolution=data.get("resolution"),
        resolution_summary=data.get("resolution_summary"),
        outcome=data.get("outcome"),
    )


with open("data/ingestion/demo/support_tickets.json", "r") as file:
    tickets = json.load(file)


normalized_tickets = []

for ticket in tickets:
    normalized_ticket = normalize_ticket(ticket)
    normalized_tickets.append(normalized_ticket)


if __name__ == "__main__":
    print("Total normalized tickets:", len(normalized_tickets))
