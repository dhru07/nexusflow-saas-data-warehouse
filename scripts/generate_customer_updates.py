#!/usr/bin/env python3
"""Create a deterministic batch of customer updates for the NexusFlow SCD2 demo."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("data/generated/customers.jsonl")
DEFAULT_OUTPUT = Path("data/incremental/batch_002/customers.jsonl")
BATCH_ID = "batch_002"
SIMULATED_UPDATE_AT = "2026-11-07T12:00:00+00:00"

INDUSTRIES = [
    "Technology",
    "Healthcare",
    "Financial Services",
    "Retail",
    "Manufacturing",
    "Education",
    "Professional Services",
]
SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]


def parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def business_hash(record: dict[str, Any]) -> str:
    excluded = {
        "batch_id",
        "ingested_at",
        "source_updated_at",
        "record_hash",
        "is_deleted",
    }
    business_fields = {k: v for k, v in record.items() if k not in excluded}
    payload = json.dumps(
        business_fields,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def read_latest_customers(path: Path) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            customer_id = row["customer_id"]
            if customer_id not in latest:
                latest[customer_id] = row
                continue

            current = latest[customer_id]
            candidate_key = (
                parse_timestamp(row.get("ingested_at")),
                parse_timestamp(row.get("source_updated_at")),
                str(row.get("batch_id", "")),
            )
            current_key = (
                parse_timestamp(current.get("ingested_at")),
                parse_timestamp(current.get("source_updated_at")),
                str(current.get("batch_id", "")),
            )
            if candidate_key > current_key:
                latest[customer_id] = row

    if not latest:
        raise ValueError(f"No customer records found in {path}")
    return latest


def build_updates(
    customers: dict[str, dict[str, Any]], update_count: int
) -> list[dict[str, Any]]:
    if update_count < 1:
        raise ValueError("--count must be at least 1")
    if update_count > len(customers):
        raise ValueError(
            f"Requested {update_count} updates, but only {len(customers)} "
            "distinct customers exist."
        )

    update_time = SIMULATED_UPDATE_AT
    selected_ids = sorted(customers)[:update_count]
    updates: list[dict[str, Any]] = []

    for index, customer_id in enumerate(selected_ids):
        updated = dict(customers[customer_id])

        current_industry = updated.get("industry")
        alternatives = [x for x in INDUSTRIES if x != current_industry]
        updated["industry"] = alternatives[index % len(alternatives)]

        current_segment = updated.get("customer_segment")
        segment_alternatives = [x for x in SEGMENTS if x != current_segment]
        updated["customer_segment"] = segment_alternatives[
            index % len(segment_alternatives)
        ]

        updated["employee_count"] = int(updated.get("employee_count") or 0) + (
            25 + (index % 10) * 10
        )
        updated["updated_at"] = update_time
        updated["batch_id"] = BATCH_ID
        updated["ingested_at"] = update_time
        updated["source_updated_at"] = update_time
        updated["is_deleted"] = False
        updated["record_hash"] = business_hash(updated)
        updates.append(updated)

    return updates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--count", type=int, default=100)
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            f"Input not found: {args.input}. Run from the repository root "
            "and ensure the original generated customer file exists."
        )

    latest = read_latest_customers(args.input)
    updates = build_updates(latest, args.count)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in updates:
            handle.write(json.dumps(row, default=str) + "\n")

    print(f"Distinct customers read: {len(latest):,}")
    print(f"Customer update records: {len(updates):,}")
    print(f"Batch ID: {BATCH_ID}")
    print(f"Simulated source update timestamp: {SIMULATED_UPDATE_AT}")
    print(f"Output: {args.output}")
    print("These are updates to existing customer IDs, not new customers.")


if __name__ == "__main__":
    main()
