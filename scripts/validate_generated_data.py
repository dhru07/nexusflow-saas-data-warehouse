
import json
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path("data/generated")

PRIMARY_KEYS = {
    "customers": "customer_id",
    "users": "user_id",
    "plans": "plan_id",
    "subscriptions": "subscription_id",
    "invoices": "invoice_id",
    "payments": "payment_id",
    "product_events": "event_id",
    "support_tickets": "ticket_id",
}

EXPECTED_INVALID_EVENTS = 40

tables = {}
unique_records = {}
failed_checks = []


def check(condition, message):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {message}")

    if not condition:
        failed_checks.append(message)


# 1. Load all source tables and validate metadata
print("\n" + "=" * 65)
print("1. FILE AND METADATA VALIDATION")
print("=" * 65)

for table, pk in PRIMARY_KEYS.items():
    path = DATA_DIR / f"{table}.jsonl"

    with path.open() as file:
        rows = [json.loads(line) for line in file if line.strip()]

    tables[table] = rows

    metadata_fields = {
        "batch_id",
        "ingested_at",
        "source_updated_at",
        "record_hash",
        "is_deleted",
    }

    missing_metadata = sum(
        not metadata_fields.issubset(row.keys())
        for row in rows
    )

    check(missing_metadata == 0, f"{table}: metadata present")

    records_by_id = defaultdict(list)

    for row in rows:
        records_by_id[row[pk]].append(row)

    unique_records[table] = records_by_id

    print(
        f"{table:18} | rows={len(rows):7,} "
        f"| unique IDs={len(records_by_id):7,} "
        f"| duplicates={len(rows) - len(records_by_id):5,}"
    )


# 2. Validate duplicate consistency
print("\n" + "=" * 65)
print("2. DUPLICATE VALIDATION")
print("=" * 65)

for table, records_by_id in unique_records.items():
    inconsistent_hashes = 0

    for records in records_by_id.values():
        hashes = {row["record_hash"] for row in records}

        if len(hashes) > 1:
            inconsistent_hashes += 1

    check(
        inconsistent_hashes == 0,
        f"{table}: duplicate records retain consistent hashes",
    )


# 3. Build reference sets
customers = set(unique_records["customers"])
users = set(unique_records["users"])
plans = set(unique_records["plans"])
subscriptions = set(unique_records["subscriptions"])
invoices = set(unique_records["invoices"])

user_to_customer = {
    user_id: records[0]["customer_id"]
    for user_id, records in unique_records["users"].items()
}


# 4. Validate foreign keys
print("\n" + "=" * 65)
print("3. FOREIGN KEY VALIDATION")
print("=" * 65)

checks = {
    "Users -> Customers": sum(
        r["customer_id"] not in customers
        for r in tables["users"]
    ),
    "Subscriptions -> Customers": sum(
        r["customer_id"] not in customers
        for r in tables["subscriptions"]
    ),
    "Subscriptions -> Plans": sum(
        r["plan_id"] not in plans
        for r in tables["subscriptions"]
    ),
    "Invoices -> Subscriptions": sum(
        r["subscription_id"] not in subscriptions
        for r in tables["invoices"]
    ),
    "Payments -> Invoices": sum(
        r["invoice_id"] not in invoices
        for r in tables["payments"]
    ),
    "Tickets -> Customers": sum(
        r["customer_id"] not in customers
        for r in tables["support_tickets"]
    ),
}

for relationship, invalid_count in checks.items():
    check(
        invalid_count == 0,
        f"{relationship}: {invalid_count} invalid references",
    )


# 5. Validate intentional invalid product events
print("\n" + "=" * 65)
print("4. PRODUCT EVENT QUALITY VALIDATION")
print("=" * 65)

invalid_event_ids = {
    row["event_id"]
    for row in tables["product_events"]
    if row["user_id"] not in users
}

check(
    len(invalid_event_ids) == EXPECTED_INVALID_EVENTS,
    f"Expected {EXPECTED_INVALID_EVENTS} invalid event IDs; found {len(invalid_event_ids)}",
)

# Check customer ownership for events with valid users.
mismatched_customers = {
    row["event_id"]
    for row in tables["product_events"]
    if row["user_id"] in users
    and row["customer_id"] != user_to_customer[row["user_id"]]
}

check(
    len(mismatched_customers) == 0,
    f"Valid event user/customer relationships: {len(mismatched_customers)} mismatches",
)


# 6. Final result
print("\n" + "=" * 65)
print("VALIDATION SUMMARY")
print("=" * 65)

if failed_checks:
    print(f"\n{len(failed_checks)} CHECK(S) FAILED:")
    for failure in failed_checks:
        print(f" - {failure}")
    raise SystemExit(1)

print("\nAll validation checks passed.")
