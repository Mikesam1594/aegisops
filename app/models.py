from dataclasses import dataclass
from typing import Optional


@dataclass
class SupportTicket:
    ticket_id: str
    customer_id: Optional[str]
    source: str
    product: Optional[str]
    title: str
    description: str
    error_message: Optional[str]
    environment: str
    recent_change: Optional[str]
    impact: str
    category: Optional[str]
    priority: str
    status: str
    created_at: str
    resolved_at: Optional[str]
    resolution_time_hours: Optional[float]
    escalated: Optional[bool]
    technician_investigation: Optional[str]
    resolution: Optional[str]
    resolution_summary: Optional[str]
    outcome: Optional[str]
