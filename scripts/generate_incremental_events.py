#!/usr/bin/env python3
"""Generate a controlled batch of new, valid, late-arriving product events."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DEFAULT_USERS = Path("data/generated/users.jsonl")
DEFAULT_OUTPUT = Path("data/incremental/batch_003/product_events.jsonl")
BATCH_ID = "batch_003"
SEED = 20261106


def read_unique_users(path: Path) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            latest[row["user_id"]] = row
    return list(latest.values())


def make_hash(record: dict[str, Any]) -> str:
    excluded = {
        "batch_id", "ingested_at", "source_updated_at",
        "record_hash", "is_deleted",
    }
    business = {k: v for k, v in record.items() if k not in excluded}
    payload = json.dumps(business, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=Path, default=DEFAULT_USERS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--late-days", type=int, default=14)
    args = parser.parse_args()

    if args.count < 1:
        raise ValueError("--count must be at least 1")
    if args.late_days < 1:
        raise ValueError("--late-days must be at least 1")
    if not args.users.exists():
        raise FileNotFoundError(f"User source file not found: {args.users}")

    users = read_unique_users(args.users)
    if not users:
        raise ValueError("No users found in input file")

    rng = random.Random(SEED)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    event_types = ["login", "feature_used", "report_exported", "integration_connected"]
    features = ["dashboard", "reporting", "automation", "integrations", "collaboration"]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for index in range(args.count):
            user = users[index % len(users)]
            # Event time is deliberately older than ingestion time:
            # these records simulate late-arriving events.
            age_days = rng.randint(1, args.late_days)
            event_time = now - timedelta(days=age_days, hours=rng.randint(0, 23))
            row: dict[str, Any] = {
                "event_id": f"EVT_BATCH003_{index + 1:06d}",
                "user_id": user["user_id"],
                "customer_id": user["customer_id"],
                "event_type": rng.choice(event_types),
                "feature_name": rng.choice(features),
                "event_timestamp": event_time.isoformat(),
                "event_properties": {
                    "source": "incremental_demo",
                    "is_late_arrival": True,
                    "sequence": index + 1,
                },
                "batch_id": BATCH_ID,
                "ingested_at": now.isoformat(),
                "source_updated_at": now.isoformat(),
                "is_deleted": False,
            }
            row["record_hash"] = make_hash(row)
            handle.write(json.dumps(row, separators=(",", ":"), default=str) + "\n")

    print(f"Unique users available: {len(users):,}")
    print(f"New product events generated: {args.count:,}")
    print(f"Batch ID: {BATCH_ID}")
    print(f"Event-time lookback: up to {args.late_days} days")
    print(f"Ingestion timestamp: {now.isoformat()}")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
