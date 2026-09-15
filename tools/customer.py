from typing import Optional

from langchain_core.tools import tool
from app.customer_profile import customer_profiles


@tool
def get_customer_profile(customer_id: Optional[str] = None) -> dict:
    """Retrieve the support profile for a customer or all customers."""

    if customer_id is None:
        return {
            "customers": [
                {
                    "customer_id": customer_id,
                    "profile": profile,
                }
                for customer_id, profile in customer_profiles.items()
            ]
        }

    profile = customer_profiles.get(customer_id)

    if profile is None:
        return {
            "customer_id": customer_id,
            "message": "No historical tickets found for this customer."
        }

    return {
        "customer_id": customer_id,
        "profile": profile,
    }


if __name__ == "__main__":
    result = get_customer_profile.invoke({"customer_id": "CUSTOMER-001"})
    print(result)
