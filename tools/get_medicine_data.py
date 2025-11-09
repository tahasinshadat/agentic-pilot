"""
Medicine Data Tool - Get medication purchase history and insights.
Returns comprehensive medication data including purchase history, refill alerts, and pricing insights.
"""

import json
from typing import Dict, Any, Optional
from tools.medicine_data.medicine_data import sync_user_transactions, get_assistant_snapshot


def get_medicine_data(
    external_user_id: Optional[str] = None,
    sync_first: bool = True
) -> Dict[str, Any]:
    """
    Get comprehensive medication data for the user.

    This function returns:
    - Medication purchase history from Amazon, Walmart, Target, etc.
    - Refill status and upcoming refill dates
    - Price history and pricing insights
    - Spending analysis
    - Alerts for overdue medications or price spikes

    Args:
        external_user_id: User ID (defaults to configured default user)
        sync_first: Whether to sync latest data before returning snapshot (default: True)

    Returns:
        Dictionary containing:
        {
            "user": {...},  # User information
            "generated_at": "2024-...",  # Timestamp
            "sections": {
                "medications": {...},  # Medication insights with refill status
                "alerts": {...},  # Refill alerts and price spike warnings
                "spending": {...},  # Spending analysis by month and merchant
                "price_benchmarks": {...}  # Price comparisons with market averages
            }
        }

    Example response for medications:
    {
        "type": "medication",
        "medication": {
            "name": "Ibuprofen 200mg Tablets 100 count",
            "sku": "IBU200"
        },
        "status": "ok",  # or "approaching", "late", "overdue"
        "timing": {
            "last_purchase_date": "2024-12-15T10:30:00Z",
            "next_refill_date": "2025-01-15T10:30:00Z",
            "days_remaining": 25
        },
        "price": {
            "latest": 8.99,
            "average": 8.50,
            "reference": {"amount": 7.50, "overpriced": true}
        },
        "recommendations": ["compare_prices"]
    }
    """
    try:
        # Sync latest data if requested
        if sync_first:
            print("[MedicineTool] Syncing latest transaction data...")
            sync_result = sync_user_transactions(
                external_user_id=external_user_id,
                source=None,  # Uses default from .env (DATA_SOURCE=local)
                limit=25
            )
            print(f"[MedicineTool] Sync complete: {json.dumps(sync_result['summary'], indent=2)}")

        # Get comprehensive snapshot
        print("[MedicineTool] Generating medication insights snapshot...")
        snapshot = get_assistant_snapshot(external_user_id=external_user_id)

        print(f"[MedicineTool] Snapshot generated with {len(snapshot.get('sections', {}).get('medications', {}).get('insights', []))} medications")

        return {
            "success": True,
            "data": snapshot
        }

    except Exception as e:
        print(f"[MedicineTool] Error: {e}")
        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve medication data. The data source may not be available."
        }
