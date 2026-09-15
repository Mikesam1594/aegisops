from app.ml import historical_records


customer_profiles = {}

for record in historical_records:
    customer_id = record["customer_id"]

    if customer_id not in customer_profiles:
        customer_profiles[customer_id] = {
            "historical_ticket_count": 0,
            "historical_escalation_count": 0,
            "resolution_times": [],
        }

    customer_profiles[customer_id]["historical_ticket_count"] += 1

    if record["escalated"] is True:
        customer_profiles[customer_id]["historical_escalation_count"] += 1

    if record["resolution_time_hours"] is not None:
        customer_profiles[customer_id]["resolution_times"].append(
            record["resolution_time_hours"]
        )


for customer_id, profile in customer_profiles.items():
    profile["historical_escalation_rate"] = (
        profile["historical_escalation_count"]
        / profile["historical_ticket_count"]
    )

    profile["average_resolution_time"] = (
        sum(profile["resolution_times"])
        / len(profile["resolution_times"])
        if profile["resolution_times"]
        else None
    )


for customer_id, profile in customer_profiles.items():
    escalation_rate = profile["historical_escalation_rate"]

    if profile["average_resolution_time"] is None:
        resolution_factor = 0
    else:
        resolution_factor = min(
            profile["average_resolution_time"] / 72,
            1,
        )

    vulnerability_score = (
        escalation_rate * 0.60
        + resolution_factor * 0.40
    )

    profile["vulnerability_score"] = vulnerability_score

    if vulnerability_score >= 0.70:
        profile["vulnerability_level"] = "high"
    elif vulnerability_score >= 0.40:
        profile["vulnerability_level"] = "medium"
    else:
        profile["vulnerability_level"] = "low"

