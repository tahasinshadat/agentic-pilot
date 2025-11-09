## MedTrack Toolkit

This repo is now a single Python toolkit that ingests Knot Tx-Link transactions (or the bundled mock JSON files), classifies medications, runs refill/price heuristics, and emits compact JSON that's easy for a healthcare AI assistant to parse--no Node backend or frontend required.

### Layout

```
medtrack/
  data/        Mock Tx-Link JSON (Amazon, Walmart, Target)
  toolkit.py   All ingestion + analytics helpers and a tiny CLI
  .cache/      Local user snapshots written by the toolkit
  .env         Optional configuration for sources, auth, defaults
```

### Quick start

```bash
cd medtrack
python toolkit.py demo          # sync local data + print assistant snapshot
python toolkit.py sync          # just sync (reads DATA_SOURCE)
python toolkit.py meds          # medication insights only
python toolkit.py alerts        # refill/price alerts
python toolkit.py spending      # spending summary
python toolkit.py price-benchmarks
python toolkit.py price --sku LIS20
python toolkit.py snapshot --price-sku LIS20 > snapshot.json
```

By default the toolkit reads the JSON exports under `data/` (`DATA_SOURCE=local`). To hit the Knot mock tunnel or dev endpoint, set these in `.env` (or your shell) before running:

```
DATA_SOURCE=mock            # or dev
KNOT_CLIENT_ID=...
KNOT_SECRET=...
DEFAULT_EXTERNAL_USER_ID=abc
DEFAULT_MERCHANT_IDS=44,45,12
REFERENCE_PRICE_URL=https://raw.githubusercontent.com/synthetichealth/synthea/master/src/main/resources/costs/medications.csv
REFERENCE_PRICE_MAX_AGE_DAYS=14
```

### Assistant-oriented helpers

Everything lives in `toolkit.py`, and each helper returns a structured object that can be fed directly to your AI agent:

| Function | Description |
| --- | --- |
| `sync_user_transactions(**kwargs)` | Pulls Knot Tx-Link data from `local`, `mock`, or `dev`, normalizes it, and persists it under `.cache/`. |
| `get_medication_advice(...)` | Machine-first medication objects (status, refill window, price metrics, recommendation codes). |
| `get_alert_advice(...)` | Structured alert rows (category, severity, data payload). |
| `get_spending_advice(...)` | Numeric wallet-share metrics, month deltas, and top merchants. |
| `get_price_history_insight(...)` | Raw history array plus calculated deltas and reference info. |
| `get_price_benchmark_advice(...)` | Compares the latest fill to public Synthea/NADAC averages. |
| `get_assistant_snapshot(...)` | Bundles medications, alerts, spending, benchmarks, and optional price history. |

> The benchmark helpers download and cache `medications.csv` from [Synthea](https://github.com/synthetichealth/synthea). Override `REFERENCE_PRICE_URL` if you prefer a different price API.

Typical medication record:

```json
{
  "type": "medication",
  "medication": {"name": "Lisinopril 20mg Tablets 90 count", "sku": "LIS20"},
  "status": "overdue",
  "timing": {"last_purchase_date": "2024-03-05T16:12:00Z", "next_refill_date": "2024-04-24T16:12:00Z", "days_remaining": -564},
  "price": {
    "latest": 18.72,
    "average": 9.88,
    "reference": {"amount": 8.0, "overpriced": true, "source": "synthea_medication_costs"}
  },
  "flags": {"price_spike": true, "overdue": true, "approaching": false},
  "recommendations": ["refill_now", "compare_prices"]
}
```

### Example integration

```python
from toolkit import sync_user_transactions, get_assistant_snapshot

sync_user_transactions(source="local", external_user_id="demo-user")
snapshot = get_assistant_snapshot(external_user_id="demo-user")

med = snapshot["sections"]["medications"]["insights"][0]
if "refill_now" in med["recommendations"]:
    print("REFILL", med["medication"]["name"], med["timing"]["days_remaining"])
```

### Notes & safety

- Insights are informational only--have a clinician confirm before taking action.
- Credentials (if you point to Knot’s APIs) stay in Python land; nothing is proxied to a UI.
- The cached files under `.cache/` are human-readable JSON. Delete them if you want to reset a user’s state.
