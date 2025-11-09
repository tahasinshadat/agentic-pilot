import csv
import io
import json
import math
import os
import re
import ssl
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

def _load_env() -> Dict[str, str]:
    env_values: Dict[str, str] = {}
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return env_values
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_values[key.strip()] = value.strip().strip('"').strip("'")
    return env_values


ENV = _load_env()

_REFERENCE_PRICE_CACHE: Dict[str, Any] = {}


def env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key) or ENV.get(key, default)

REFERENCE_PRICE_URL = env(
    "REFERENCE_PRICE_URL",
    "https://raw.githubusercontent.com/synthetichealth/synthea/master/src/main/resources/costs/medications.csv",
)
REFERENCE_PRICE_CACHE_PATH = CACHE_DIR / "reference_prices.json"
REFERENCE_PRICE_MAX_AGE_DAYS = int(env("REFERENCE_PRICE_MAX_AGE_DAYS", "14"))
MERCHANT_CATALOG = [
    {"id": 44, "name": "Amazon"},
    {"id": 45, "name": "Walmart"},
    {"id": 12, "name": "Target"},
    {"id": 165, "name": "Costco"},
    {"id": 19, "name": "Doordash"},
    {"id": 40, "name": "Instacart"},
    {"id": 36, "name": "Ubereats"},
]
MERCHANT_MAP = {merchant["id"]: merchant["name"] for merchant in MERCHANT_CATALOG}

DEFAULT_EXTERNAL_USER_ID = env("DEFAULT_EXTERNAL_USER_ID", "abc")
DEFAULT_USER_NAME = env("DEFAULT_USER_NAME", "MedTrack Demo User")
DEFAULT_MERCHANT_IDS = [
    int(part.strip())
    for part in env("DEFAULT_MERCHANT_IDS", "44,45,12").split(",")
    if part.strip().isdigit()
]
DATA_SOURCE = env("DATA_SOURCE", "local").lower()
KNOT_DEV_URL = f"{env('KNOT_DEV_URL', 'https://development.knotapi.com')}/transactions/sync"
KNOT_MOCK_URL = f"{env('KNOT_MOCK_URL', 'https://knot.tunnel.tel')}/transactions/sync"
KNOT_BASIC_AUTH = env("KNOT_BASIC_AUTH", None)
if not KNOT_BASIC_AUTH:
    client_id = env("KNOT_CLIENT_ID", "")
    secret = env("KNOT_SECRET", "")
    if client_id and secret:
        import base64

        KNOT_BASIC_AUTH = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
MEDICATION_KEYWORDS = [
    "mg",
    "mcg",
    "tablet",
    "tab",
    "tabs",
    "capsule",
    "capsules",
    "pill",
    "caplet",
    "caplets",
    "ointment",
    "cream",
    "gel",
    "drops",
    "syrup",
    "vitamin",
    "supplement",
    "rx",
    "pain relief",
    "allergy",
    "sleep aid",
    "blood pressure",
    "cholesterol",
    "antibiotic",
]

INGREDIENT_KEYWORDS = {
    "acetaminophen": ["acetaminophen", "tylenol"],
    "ibuprofen": ["ibuprofen", "advil", "motrin"],
    "naproxen": ["naproxen", "aleve"],
    "omeprazole": ["omeprazole", "prilosec"],
    "lansoprazole": ["lansoprazole", "prevacid"],
    "loratadine": ["loratadine", "claritin"],
    "cetirizine": ["cetirizine", "zyrtec"],
    "diphenhydramine": ["diphenhydramine", "benadryl"],
    "simvastatin": ["simvastatin"],
    "atorvastatin": ["atorvastatin", "lipitor"],
    "amlodipine": ["amlodipine"],
    "metformin": ["metformin"],
    "insulin": ["insulin"],
    "multivitamin": ["multivitamin", "multi-vitamin"],
}


def normalize_medication_name(name: str = "") -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", name.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def classify_medication(name: str = "") -> Dict[str, Optional[str]]:
    normalized = normalize_medication_name(name)
    if not normalized:
        return {"is_medication": False, "normalized_name": None, "ingredient_key": None}
    ingredient_key = None
    for key, values in INGREDIENT_KEYWORDS.items():
        if any(term in normalized for term in values):
            ingredient_key = key
            break
    is_med = bool(ingredient_key) or any(keyword in normalized for keyword in MEDICATION_KEYWORDS)
    return {
        "is_medication": is_med,
        "normalized_name": normalized if is_med else None,
        "ingredient_key": ingredient_key,
    }


def estimate_days_supply_from_quantity(quantity: Optional[float]) -> int:
    if not quantity or quantity <= 0:
        return 30
    if quantity >= 120:
        return 90
    if quantity >= 90:
        return 60
    if quantity >= 60:
        return 45
    if quantity >= 30:
        return 30
    if quantity >= 14:
        return 21
    return 30


def _safe_float(value: Optional[str]) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _load_reference_prices_from_disk() -> Optional[Dict[str, Any]]:
    if not REFERENCE_PRICE_CACHE_PATH.exists():
        return None
    try:
        payload = json.loads(REFERENCE_PRICE_CACHE_PATH.read_text(encoding="utf-8"))
        return payload
    except json.JSONDecodeError:
        return None


def _write_reference_prices_to_disk(data: Dict[str, Any]) -> None:
    REFERENCE_PRICE_CACHE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _download_reference_price_records() -> Optional[List[Dict[str, Any]]]:
    try:
        with urllib.request.urlopen(REFERENCE_PRICE_URL, timeout=30) as response:
            raw_text = response.read().decode("utf-8", errors="ignore")
    except Exception:
        return None
    reader = csv.DictReader(io.StringIO(raw_text))
    records: List[Dict[str, Any]] = []
    for row in reader:
        code = row.get("CODE")
        if not code:
            continue
        description = row.get("COMMENTS") or ""
        record = {
            "code": code.strip(),
            "min": _safe_float(row.get("MIN")),
            "mode": _safe_float(row.get("MODE")),
            "max": _safe_float(row.get("MAX")),
            "description": description.strip(),
            "description_norm": normalize_medication_name(description),
        }
        records.append(record)
    return records


def _reference_price_cache_is_stale(timestamp: Optional[str]) -> bool:
    if not timestamp:
        return True
    try:
        cached_at = datetime.fromisoformat(timestamp)
    except ValueError:
        return True
    return datetime.now(timezone.utc) - cached_at > timedelta(days=REFERENCE_PRICE_MAX_AGE_DAYS)


def _ensure_reference_price_index() -> Dict[str, Any]:
    global _REFERENCE_PRICE_CACHE  # pylint: disable=global-statement
    if _REFERENCE_PRICE_CACHE:
        return _REFERENCE_PRICE_CACHE

    payload = _load_reference_prices_from_disk()
    if not payload or _reference_price_cache_is_stale(payload.get("fetched_at")):
        records = _download_reference_price_records()
        if records:
            payload = {"fetched_at": datetime.now(timezone.utc).isoformat(), "records": records}
            _write_reference_prices_to_disk(payload)
    if not payload:
        payload = {"fetched_at": None, "records": []}

    by_code = {record["code"]: record for record in payload["records"]}
    by_name = {record["description_norm"]: record for record in payload["records"] if record["description_norm"]}
    _REFERENCE_PRICE_CACHE = {
        "records": payload["records"],
        "by_code": by_code,
        "by_name": by_name,
    }
    return _REFERENCE_PRICE_CACHE


def lookup_reference_price(drug_name: Optional[str] = None, rxnorm_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
    index = _ensure_reference_price_index()
    if rxnorm_code and rxnorm_code in index["by_code"]:
        return index["by_code"][rxnorm_code]
    if not drug_name:
        return None
    normalized = normalize_medication_name(drug_name)
    if not normalized:
        return None
    if normalized in index["by_name"]:
        return index["by_name"][normalized]
    # fallback: substring match
    for record in index["records"]:
        norm = record["description_norm"]
        if not norm:
            continue
        if normalized in norm or norm in normalized:
            return record
    return None

def _user_file(external_user_id: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", external_user_id)
    return CACHE_DIR / f"{safe}_transactions.json"


def _default_user(external_user_id: str) -> Dict[str, Any]:
    return {
        "id": abs(hash(external_user_id)) % 1_000_000_000,
        "name": DEFAULT_USER_NAME,
        "external_user_id": external_user_id,
    }


def _load_user_state(external_user_id: str) -> Dict[str, Any]:
    path = _user_file(external_user_id)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"user": _default_user(external_user_id), "transactions": []}


def _save_user_state(external_user_id: str, state: Dict[str, Any]) -> None:
    _user_file(external_user_id).write_text(json.dumps(state, indent=2), encoding="utf-8")

def _find_local_file(merchant_id: int) -> Path:
    matches = list(DATA_DIR.glob(f"*_{merchant_id}_*.json"))
    if not matches:
        raise FileNotFoundError(f"Missing mock data for merchant {merchant_id} in {DATA_DIR}")
    return matches[0]


def _load_local_transactions(merchant_id: int, limit: int) -> List[Dict[str, Any]]:
    data = json.loads(_find_local_file(merchant_id).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Local data for merchant {merchant_id} must be a list")
    return data[:limit]


def _post_json(url: str, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Any:
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=req_headers,
        method="POST",
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, context=context, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _fetch_transactions(merchant_id: int, external_user_id: str, limit: int, source: str) -> List[Dict[str, Any]]:
    normalized = source.lower()
    if normalized == "local":
        return _load_local_transactions(merchant_id, limit)
    if normalized == "mock":
        payload = _post_json(
            KNOT_MOCK_URL,
            {"merchant_id": merchant_id, "external_user_id": external_user_id, "limit": limit},
        )
        return payload if isinstance(payload, list) else payload.get("transactions", [])
    if normalized == "dev":
        headers = {"Authorization": f"Basic {KNOT_BASIC_AUTH}"} if KNOT_BASIC_AUTH else {}
        payload = _post_json(
            KNOT_DEV_URL,
            {"merchant_id": merchant_id, "external_user_id": external_user_id, "limit": limit},
            headers=headers,
        )
        return payload if isinstance(payload, list) else payload.get("transactions", [])
    raise ValueError(f"Unsupported data source '{source}'")

def _safe_date(value: Optional[str]) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.now(timezone.utc)


def _resolve_external_id(transaction: Dict[str, Any], merchant_id: int) -> str:
    for key in ("externalId", "external_id", "orderId", "order_id"):
        if transaction.get(key):
            return str(transaction[key])
    fallback = transaction.get("url") or transaction.get("dateTime") or transaction.get("orderDate")
    return f"{merchant_id}-{fallback or datetime.now(timezone.utc).isoformat()}"


def _derive_total(transaction: Dict[str, Any]) -> Optional[float]:
    for key in ("total", "amount"):
        value = transaction.get(key)
        if isinstance(value, (int, float)):
            return round(float(value), 2)
    items = transaction.get("items")
    if not isinstance(items, list):
        return None
    total = 0.0
    for item in items:
        price = item.get("price") or 0
        quantity = item.get("quantity") or 1
        total += float(price) * float(quantity)
    return round(total, 2) if total > 0 else None


def _normalize_transaction(raw: Dict[str, Any], merchant_id: int, source: str) -> Dict[str, Any]:
    order_date = _safe_date(raw.get("dateTime") or raw.get("orderDate") or raw.get("ordered_at"))
    normalized_items = []
    for item in raw.get("items", []):
        classification = classify_medication(item.get("name", ""))
        normalized_items.append(
            {
                "name": item.get("name") or "Unknown Item",
                "sku": item.get("sku"),
                "price": item.get("price"),
                "quantity": item.get("quantity"),
                "is_medication": classification["is_medication"],
                "normalized_name": classification["normalized_name"],
                "ingredient_key": classification["ingredient_key"],
            }
        )
    return {
        "external_id": _resolve_external_id(raw, merchant_id),
        "merchant_id": merchant_id,
        "merchant_name": MERCHANT_MAP.get(merchant_id, f"Merchant {merchant_id}"),
        "order_id": raw.get("orderId") or raw.get("externalId"),
        "order_date": order_date.isoformat(),
        "status": raw.get("orderStatus") or raw.get("status") or "UNKNOWN",
        "total": _derive_total(raw),
        "source": source,
        "items": normalized_items,
    }

def sync_user_transactions(
    merchant_ids: Optional[List[int]] = None,
    external_user_id: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 25,
) -> Dict[str, Any]:
    external_id = external_user_id or DEFAULT_EXTERNAL_USER_ID
    merchant_list = merchant_ids or DEFAULT_MERCHANT_IDS
    source_choice = (source or DATA_SOURCE).lower()
    if not merchant_list:
        raise ValueError("At least one merchant_id is required.")
    state = _load_user_state(external_id)
    existing = {tx["external_id"]: tx for tx in state.get("transactions", [])}
    summary = []
    for merchant_id in merchant_list:
        created = 0
        updated = 0
        try:
            raw_transactions = _fetch_transactions(merchant_id, external_id, limit, source_choice) or []
            for raw in raw_transactions:
                normalized = _normalize_transaction(raw, merchant_id, source_choice)
                if normalized["external_id"] in existing:
                    existing[normalized["external_id"]] = normalized
                    updated += 1
                else:
                    existing[normalized["external_id"]] = normalized
                    created += 1
            summary.append(
                {
                    "merchant_id": merchant_id,
                    "merchant_name": MERCHANT_MAP.get(merchant_id, f"Merchant {merchant_id}"),
                    "fetched": len(raw_transactions),
                    "created": created,
                    "updated": updated,
                }
            )
        except Exception as exc:  # pylint: disable=broad-except
            summary.append(
                {
                    "merchant_id": merchant_id,
                    "merchant_name": MERCHANT_MAP.get(merchant_id, f"Merchant {merchant_id}"),
                    "error": str(exc),
                }
            )
    transactions = sorted(existing.values(), key=lambda tx: tx["order_date"])
    state["transactions"] = transactions
    state["user"] = state.get("user") or _default_user(external_id)
    _save_user_state(external_id, state)
    return {"user": state["user"], "summary": summary}

def _load_transactions(external_user_id: str) -> Dict[str, Any]:
    state = _load_user_state(external_user_id)
    return state["user"], state.get("transactions", [])


def _line_total(item: Dict[str, Any]) -> Optional[float]:
    price = item.get("price")
    quantity = item.get("quantity") or 1
    if price is None:
        return None
    return float(price) * float(quantity)


def _group_med_items(transactions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for tx in transactions:
        for item in tx.get("items", []):
            if not item.get("is_medication"):
                continue
            key = (item.get("sku") or "").lower() or item.get("normalized_name") or normalize_medication_name(item.get("name", ""))
            if key:
                groups[key].append({"transaction": tx, "item": item})
    return groups


def _average(values: List[float]) -> Optional[float]:
    return sum(values) / len(values) if values else None

def _summarize_medication(key: str, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    sorted_entries = sorted(entries, key=lambda entry: entry["transaction"]["order_date"])
    last_entry = sorted_entries[-1]
    prices = [entry["item"].get("price") for entry in sorted_entries if isinstance(entry["item"].get("price"), (int, float))]
    quantities = [
        entry["item"].get("quantity")
        for entry in sorted_entries
        if isinstance(entry["item"].get("quantity"), (int, float)) and entry["item"].get("quantity") > 0
    ]
    price_history = [
        {"price": entry["item"].get("price"), "date": entry["transaction"].get("order_date")}
        for entry in sorted_entries
        if isinstance(entry["item"].get("price"), (int, float))
    ]
    historical_prices = prices[:-1]
    average_price = _average(historical_prices) if historical_prices else _average(prices)
    latest_price = prices[-1] if prices else None
    purchase_dates = [_safe_date(entry["transaction"].get("order_date")) for entry in sorted_entries]
    intervals = [(purchase_dates[i] - purchase_dates[i - 1]).days for i in range(1, len(purchase_dates))]
    historical_interval = _average(intervals)
    estimated_supply = historical_interval or (
        estimate_days_supply_from_quantity(quantities[-1]) if quantities else 30
    )
    next_refill = _safe_date(last_entry["transaction"].get("order_date")) + timedelta(days=round(estimated_supply))
    days_remaining = (next_refill - datetime.now(timezone.utc)).days
    price_spike = bool(average_price and latest_price and latest_price > average_price * 1.5 and len(prices) > 1)
    if days_remaining < -3:
        status = "overdue"
    elif days_remaining < 0:
        status = "late"
    elif days_remaining <= 7:
        status = "approaching"
    else:
        status = "ok"
    item = last_entry["item"]
    tx = last_entry["transaction"]
    return {
        "key": key,
        "display_name": item.get("name"),
        "sku": item.get("sku"),
        "ingredient_key": item.get("ingredient_key"),
        "merchant_id": tx["merchant_id"],
        "merchant_name": tx["merchant_name"],
        "last_purchase_date": tx["order_date"],
        "latest_price": latest_price,
        "average_price": round(average_price, 2) if average_price else None,
        "next_refill_date": next_refill.isoformat(),
        "days_remaining": days_remaining,
        "status": status,
        "total_purchases": len(sorted_entries),
        "price_history": price_history,
        "flags": {
            "price_spike": price_spike,
            "overdue": status == "overdue",
            "approaching": status == "approaching",
        },
    }

def _duplicate_medication_alerts(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        ingredient = entry["item"].get("ingredient_key")
        if ingredient:
            buckets[ingredient].append(entry)
    for ingredient, bucket_entries in buckets.items():
        sorted_entries = sorted(bucket_entries, key=lambda entry: entry["transaction"]["order_date"])
        for i in range(1, len(sorted_entries)):
            prev = sorted_entries[i - 1]
            cur = sorted_entries[i]
            days_apart = (
                _safe_date(cur["transaction"]["order_date"]) - _safe_date(prev["transaction"]["order_date"])
            ).days
            if (
                days_apart <= 14
                and prev["item"].get("sku") != cur["item"].get("sku")
                and prev["item"].get("name") != cur["item"].get("name")
            ):
                alerts.append(
                    {
                        "type": "Duplicate Medication",
                        "medication_name": ingredient,
                        "message": f"Multiple {ingredient} items purchased within {days_apart} days.",
                        "details": {
                            "first_item": prev["item"].get("name"),
                            "second_item": cur["item"].get("name"),
                            "first_date": prev["transaction"].get("order_date"),
                            "second_date": cur["transaction"].get("order_date"),
                        },
                    }
                )
    return alerts


def _medication_context(transactions: List[Dict[str, Any]]):
    groups = _group_med_items(transactions)
    summaries = []
    med_entries: List[Dict[str, Any]] = []
    for key, entries in groups.items():
        summaries.append(_summarize_medication(key, entries))
        med_entries.extend(entries)
    return summaries, med_entries

def _wrap_response(user: Dict[str, Any], insights: List[Dict[str, Any]], message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "user": user,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "insights": insights,
        "message": None if insights else message,
        "context": context,
    }


def _describe_days(days: Optional[int]) -> str:
    if days is None:
        return "an unknown amount of time"
    if days < -1:
        return f"{abs(days)} days past due"
    if days == -1:
        return "1 day past due"
    if days == 0:
        return "due today"
    if days == 1:
        return "1 day remaining"
    return f"{days} days remaining"


def _format_currency(value: Optional[float]) -> Optional[str]:
    if value is None:
        return None
    return f"${value:.2f}"

def get_medication_advice(external_user_id: Optional[str] = None) -> Dict[str, Any]:
    external_id = external_user_id or DEFAULT_EXTERNAL_USER_ID
    user, transactions = _load_transactions(external_id)
    if not transactions:
        return _wrap_response(user, [], "no_transactions")
    summaries, _ = _medication_context(transactions)
    insights = []
    for summary in summaries:
        status = summary["status"]
        recommendations = []
        if status in ("overdue", "late"):
            recommendations.append("refill_now")
        elif status == "approaching":
            recommendations.append("schedule_refill")
        if summary["flags"].get("price_spike") and "compare_prices" not in recommendations:
            recommendations.append("compare_prices")

        reference = lookup_reference_price(summary["display_name"]) or (
            lookup_reference_price(summary.get("ingredient_key")) if summary.get("ingredient_key") else None
        )
        reference_amount = None
        overpriced = False
        reference_details = None
        if reference:
            reference_details = {
                "code": reference.get("code"),
                "description": reference.get("description"),
                "min": reference.get("min"),
                "mode": reference.get("mode"),
                "max": reference.get("max"),
            }
            reference_amount = reference.get("mode") or reference.get("min") or reference.get("max")
            latest_price = summary.get("latest_price")
            if reference_amount and latest_price:
                overpriced = latest_price - reference_amount > max(1, reference_amount * 0.15)
                if overpriced and "compare_prices" not in recommendations:
                    recommendations.append("compare_prices")

        reference_payload = {
            "amount": reference_amount,
            "overpriced": overpriced,
            "source": "synthea_medication_costs" if reference else None,
            "details": reference_details,
        }
        summary.setdefault("price_context", {})["reference"] = reference_payload
        price_block = {
            "latest": summary.get("latest_price"),
            "average": summary.get("average_price"),
            "history": summary.get("price_history"),
            "reference": reference_payload,
        }

        payload = {
            "type": "medication",
            "medication": {
                "name": summary["display_name"],
                "key": summary["key"],
                "sku": summary["sku"],
                "ingredient_key": summary["ingredient_key"],
            },
            "status": status,
            "timing": {
                "last_purchase_date": summary["last_purchase_date"],
                "next_refill_date": summary["next_refill_date"],
                "days_remaining": summary["days_remaining"],
            },
            "merchant": {
                "id": summary["merchant_id"],
                "name": summary["merchant_name"],
            },
            "price": price_block,
            "total_purchases": summary["total_purchases"],
            "flags": summary["flags"],
            "recommendations": list(dict.fromkeys(recommendations)),
        }
        insights.append(payload)
    return _wrap_response(user, insights, None)
SEVERITY_BY_ALERT = {
    "Missed Refill": "critical",
    "Upcoming Refill": "warning",
    "Price Spike": "warning",
    "Duplicate Medication": "caution",
}

ALERT_ACTIONS = {
    "Missed Refill": "Reach out to the member or caregiver and arrange the missed refill.",
    "Upcoming Refill": "Plan a reminder or schedule a pickup/delivery.",
    "Price Spike": "Check for alternative pharmacies or savings programs.",
    "Duplicate Medication": "Confirm with a clinician whether both medications are still needed.",
}


def get_alert_advice(external_user_id: Optional[str] = None) -> Dict[str, Any]:
    external_id = external_user_id or DEFAULT_EXTERNAL_USER_ID
    user, transactions = _load_transactions(external_id)
    if not transactions:
        return _wrap_response(user, [], "no_transactions")
    summaries, med_entries = _medication_context(transactions)
    alerts = []
    for summary in summaries:
        status = summary["status"]
        display = summary["display_name"]
        if status in ("overdue", "late"):
            alerts.append(
                {
                    "type": "alert",
                    "category": "missed_refill",
                    "severity": "critical" if status == "overdue" else "warning",
                    "medication": display,
                    "data": {
                        "last_purchase_date": summary["last_purchase_date"],
                        "next_refill_date": summary["next_refill_date"],
                        "days_remaining": summary["days_remaining"],
                    },
                    "recommendations": ["refill_now"],
                }
            )
        elif status == "approaching":
            alerts.append(
                {
                    "type": "alert",
                    "category": "upcoming_refill",
                    "severity": "info",
                    "medication": display,
                    "data": {
                        "days_until_due": max(summary["days_remaining"], 0),
                        "next_refill_date": summary["next_refill_date"],
                    },
                    "recommendations": ["schedule_refill"],
                }
            )
        if summary["flags"]["price_spike"]:
            alerts.append(
                {
                    "type": "alert",
                    "category": "price_spike",
                    "severity": "warning",
                    "medication": display,
                    "data": {
                        "latest_price": summary["latest_price"],
                        "average_price": summary["average_price"],
                        "last_purchase_date": summary["last_purchase_date"],
                        "merchant_name": summary["merchant_name"],
                    },
                    "recommendations": ["compare_prices"],
                }
            )
    for alert in _duplicate_medication_alerts(med_entries):
        alerts.append(
            {
                "type": "alert",
                "category": "duplicate_medication",
                "severity": "caution",
                "medication": alert["medication_name"],
                "data": alert["details"],
                "recommendations": ["clinical_review"],
            }
        )
    return _wrap_response(user, alerts, None)


def get_price_benchmark_advice(external_user_id: Optional[str] = None) -> Dict[str, Any]:
    external_id = external_user_id or DEFAULT_EXTERNAL_USER_ID
    user, transactions = _load_transactions(external_id)
    if not transactions:
        return _wrap_response(user, [], "no_transactions")
    summaries, _ = _medication_context(transactions)
    insights = []
    for summary in summaries:
        reference = lookup_reference_price(summary["display_name"]) or (
            lookup_reference_price(summary.get("ingredient_key")) if summary.get("ingredient_key") else None
        )
        latest = summary.get("latest_price")
        if not reference or latest is None:
            continue
        reference_amount = reference.get("mode") or reference.get("min") or reference.get("max")
        if not reference_amount:
            continue
        delta = latest - reference_amount
        percent = round((delta / reference_amount) * 100) if reference_amount else None
        overpriced = delta > max(1, reference_amount * 0.15)
        insights.append(
            {
                "type": "price-benchmark",
                "medication": summary["display_name"],
                "overpriced": overpriced,
                "metrics": {
                    "latest_price": latest,
                    "reference_price": reference_amount,
                    "difference": delta,
                    "percent_difference": percent,
                    "reference_details": reference,
                },
                "recommendations": ["compare_prices"] if overpriced else [],
            }
        )
    return _wrap_response(user, insights, None)

def _spending_summary(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    monthly: Dict[str, Dict[str, Any]] = {}
    merchants: Dict[int, Dict[str, Any]] = {}
    medication_total = 0.0
    other_total = 0.0
    for tx in transactions:
        order_date = _safe_date(tx["order_date"])
        month_key = order_date.strftime("%Y-%m")
        if month_key not in monthly:
            monthly[month_key] = {
                "month": month_key,
                "label": order_date.strftime("%b %Y"),
                "total": 0.0,
                "medication_total": 0.0,
                "other_total": 0.0,
            }
        if tx["merchant_id"] not in merchants:
            merchants[tx["merchant_id"]] = {
                "merchant_id": tx["merchant_id"],
                "merchant_name": tx["merchant_name"],
                "total": 0.0,
                "medication_total": 0.0,
                "other_total": 0.0,
            }
        for item in tx.get("items", []):
            line_total = _line_total(item)
            if not line_total:
                continue
            is_med = item.get("is_medication", False)
            monthly[month_key]["total"] += line_total
            merchants[tx["merchant_id"]]["total"] += line_total
            if is_med:
                monthly[month_key]["medication_total"] += line_total
                merchants[tx["merchant_id"]]["medication_total"] += line_total
                medication_total += line_total
            else:
                monthly[month_key]["other_total"] += line_total
                merchants[tx["merchant_id"]]["other_total"] += line_total
                other_total += line_total
    monthly_series = [
        {
            **entry,
            "total": round(entry["total"], 2),
            "medication_total": round(entry["medication_total"], 2),
            "other_total": round(entry["other_total"], 2),
        }
        for entry in sorted(monthly.values(), key=lambda entry: entry["month"])
    ]
    merchant_series = [
        {
            **entry,
            "total": round(entry["total"], 2),
            "medication_total": round(entry["medication_total"], 2),
            "other_total": round(entry["other_total"], 2),
        }
        for entry in sorted(merchants.values(), key=lambda entry: entry["total"], reverse=True)
    ]
    return {
        "monthly": monthly_series,
        "merchants": merchant_series,
        "totals": {
            "medication": round(medication_total, 2),
            "other": round(other_total, 2),
            "overall": round(medication_total + other_total, 2),
        },
    }


def get_spending_advice(external_user_id: Optional[str] = None) -> Dict[str, Any]:
    external_id = external_user_id or DEFAULT_EXTERNAL_USER_ID
    user, transactions = _load_transactions(external_id)
    if not transactions:
        return _wrap_response(user, [], "no_transactions")
    summary = _spending_summary(transactions)
    totals = summary["totals"]
    med_share = round((totals["medication"] / totals["overall"]) * 100) if totals["overall"] else 0
    insights = [
        {
            "type": "spending",
            "metric": "medication_share",
            "values": {
                "medication": totals["medication"],
                "overall": totals["overall"],
                "percent": med_share,
            },
            "recommendations": ["optimize_medication_spend"] if med_share >= 70 else [],
        }
    ]
    if len(summary["monthly"]) >= 2:
        prev = summary["monthly"][-2]
        latest = summary["monthly"][-1]
        delta = latest["total"] - prev["total"]
        direction = "increased" if delta > 0 else "decreased" if delta < 0 else "stayed flat"
        percent = round(abs(delta) / prev["total"] * 100) if prev["total"] else None
        insights.append(
            {
                "type": "spending",
                "metric": "monthly_trend",
                "values": {"previous": prev, "latest": latest, "delta": delta, "percent": percent},
                "direction": direction,
                "recommendations": ["review_recent_transactions"] if delta > 0 else [],
            }
        )
    if summary["merchants"]:
        top = summary["merchants"][0]
        insights.append(
            {
                "type": "spending",
                "metric": "top_merchant",
                "values": top,
                "recommendations": ["request_loyalty_savings"],
            }
        )
    return _wrap_response(user, insights, None, context=summary)

def get_price_history_insight(
    key: Optional[str] = None,
    sku: Optional[str] = None,
    external_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    external_id = external_user_id or DEFAULT_EXTERNAL_USER_ID
    user, transactions = _load_transactions(external_id)
    if not transactions:
        return _wrap_response(user, [], "Sync data first to unlock price history.")
    if not key and not sku:
        raise ValueError("Provide a medication key or SKU.")
    normalized_key = (key or "").lower()
    history = []
    for tx in transactions:
        for item in tx.get("items", []):
            matched = False
            if sku and item.get("sku") == sku:
                matched = True
            elif normalized_key and (
                item.get("normalized_name") == normalized_key
                or normalize_medication_name(item.get("name", "")) == normalized_key
            ):
                matched = True
            if matched:
                history.append(
                    {
                        "price": item.get("price"),
                        "quantity": item.get("quantity"),
                        "date": tx["order_date"],
                        "merchant_id": tx["merchant_id"],
                        "merchant_name": tx["merchant_name"],
                    }
                )
    priced = [entry for entry in history if isinstance(entry["price"], (int, float))]
    stats = {}
    if len(priced) >= 2:
        first = priced[0]
        last = priced[-1]
        delta = (last["price"] or 0) - (first["price"] or 0)
        percent = round((delta / first["price"]) * 100) if first["price"] else None
        stats = {
            "direction": "increase" if delta > 0 else "decrease" if delta < 0 else "flat",
            "absolute_change": delta,
            "percent_change": percent,
            "points": len(priced),
        }
    elif priced:
        stats = {
            "direction": "single_point",
            "absolute_change": 0,
            "percent_change": None,
            "points": 1,
        }
    reference = None
    if key:
        reference = lookup_reference_price(key)
    if not reference and sku:
        reference = lookup_reference_price(sku)
    insight = {
        "type": "price_history",
        "identifier": key or sku,
        "history": history,
        "stats": stats,
        "reference": reference,
    }
    insights = [insight] if history else []
    return _wrap_response(user, insights, "no_history", context={"history_points": len(history)})

def get_assistant_snapshot(
    external_user_id: Optional[str] = None,
    price_key: Optional[str] = None,
    price_sku: Optional[str] = None,
) -> Dict[str, Any]:
    external_id = external_user_id or DEFAULT_EXTERNAL_USER_ID
    meds = get_medication_advice(external_id)
    alerts = get_alert_advice(external_id)
    spending = get_spending_advice(external_id)
    benchmarks = get_price_benchmark_advice(external_id)
    snapshot = {
        "user": meds["user"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": {
            "medications": meds,
            "alerts": alerts,
            "spending": spending,
            "price_benchmarks": benchmarks,
        },
    }
    if price_key or price_sku:
        snapshot["sections"]["price_history"] = get_price_history_insight(
            key=price_key,
            sku=price_sku,
            external_user_id=external_id,
        )
    return snapshot


def run_demo() -> None:
    print("Syncing local demo data...")
    summary = sync_user_transactions(source="local")
    print("Sync summary:", json.dumps(summary["summary"], indent=2))
    snapshot = get_assistant_snapshot()
    print("Assistant-ready insights:\n", json.dumps(snapshot, indent=2))


def medicine_data():
    import argparse

    parser = argparse.ArgumentParser(description="MedTrack assistant toolkit")
    parser.add_argument(
        "command",
        nargs="?",
        default="snapshot",
        choices=["sync", "meds", "alerts", "spending", "price", "price-benchmarks", "snapshot", "demo"],
    )
    parser.add_argument("--external-user-id", dest="external_user_id")
    parser.add_argument("--source")
    parser.add_argument("--merchant-ids")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--price-key", dest="price_key")
    parser.add_argument("--price-sku", dest="price_sku")
    parser.add_argument("--output")
    args = parser.parse_args()

    merchant_ids = (
        [int(part.strip()) for part in args.merchant_ids.split(",") if part.strip()]
        if args.merchant_ids
        else None
    )

    if args.command == "sync":
        result = sync_user_transactions(
            merchant_ids=merchant_ids,
            external_user_id=args.external_user_id,
            source=args.source,
            limit=args.limit,
        )
    elif args.command == "meds":
        result = get_medication_advice(args.external_user_id)
    elif args.command == "alerts":
        result = get_alert_advice(args.external_user_id)
    elif args.command == "spending":
        result = get_spending_advice(args.external_user_id)
    elif args.command == "price":
        result = get_price_history_insight(
            key=args.price_key,
            sku=args.price_sku,
            external_user_id=args.external_user_id,
        )
    elif args.command == "price-benchmarks":
        result = get_price_benchmark_advice(args.external_user_id)
    elif args.command == "demo":
        run_demo()
        return
    else:
        result = get_assistant_snapshot(
            external_user_id=args.external_user_id,
            price_key=args.price_key,
            price_sku=args.price_sku,
        )

    output = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote output to {args.output}")
    else:
        print(output)