
import argparse
import hashlib
import json
import random
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from faker import Faker

SEED = 42
AS_OF = date(2026, 11, 6)
INGESTED_AT = datetime(2026, 11, 6, 12, 0, tzinfo=timezone.utc)

fake = Faker()
Faker.seed(SEED)
random.seed(SEED)

PLANS = [
    {"plan_id": "PLAN_001", "plan_name": "Starter", "monthly_price": 29.00,
     "billing_interval": "monthly", "max_users": 10},
    {"plan_id": "PLAN_002", "plan_name": "Growth", "monthly_price": 99.00,
     "billing_interval": "monthly", "max_users": 50},
    {"plan_id": "PLAN_003", "plan_name": "Business", "monthly_price": 249.00,
     "billing_interval": "monthly", "max_users": 200},
    {"plan_id": "PLAN_004", "plan_name": "Enterprise", "monthly_price": 799.00,
     "billing_interval": "monthly", "max_users": None},
    {"plan_id": "PLAN_005", "plan_name": "Annual Business", "monthly_price": 199.00,
     "billing_interval": "annual", "max_users": 200},
]

INDUSTRIES = [
    "Technology", "Healthcare", "Finance", "Education", "Retail",
    "Manufacturing", "Consulting", "Media", "Logistics", "Real Estate",
]
COUNTRIES = [
    "India", "United States", "United Kingdom", "Germany",
    "Canada", "Australia", "Singapore",
]
ROLES = ["admin", "manager", "analyst", "member", "viewer"]
EVENTS = [
    ("login", "authentication"),
    ("dashboard_viewed", "dashboard"),
    ("report_created", "reporting"),
    ("report_exported", "reporting"),
    ("integration_connected", "integrations"),
    ("workflow_created", "automation"),
    ("workflow_executed", "automation"),
    ("user_invited", "team_management"),
    ("settings_updated", "settings"),
]
TICKET_CATEGORIES = [
    "billing", "technical", "account", "integration", "feature_request"
]
PAYMENT_METHODS = ["card", "bank_transfer", "upi"]
CURRENCIES = ["USD", "INR", "GBP", "EUR", "CAD", "AUD", "SGD"]


def iso(value):
    """Serialize dates and timestamps as ISO-8601 strings."""
    return value.isoformat()


def random_date(start, end):
    """Return a random date in an inclusive date range."""
    if end < start:
        end = start
    return start + timedelta(days=random.randint(0, (end - start).days))


def random_timestamp(start, end):
    """Return a random UTC timestamp in an inclusive range."""
    start_dt = datetime.combine(start, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(end, time.max, tzinfo=timezone.utc)
    seconds = int((end_dt - start_dt).total_seconds())
    return start_dt + timedelta(seconds=random.randint(0, max(seconds, 0)))


def record_hash(record):
    """Hash business fields only, excluding ingestion metadata."""
    excluded = {
        "batch_id", "ingested_at", "source_updated_at",
        "record_hash", "is_deleted",
    }
    business_data = {
        key: value for key, value in record.items()
        if key not in excluded
    }
    payload = json.dumps(
        business_data, sort_keys=True, separators=(",", ":"), default=str
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def add_metadata(record, source_updated_at, batch_id="batch_001"):
    record["batch_id"] = batch_id
    record["ingested_at"] = iso(INGESTED_AT)
    record["source_updated_at"] = iso(source_updated_at)
    record["is_deleted"] = False
    record["record_hash"] = record_hash(record)
    return record


def write_jsonl(records, output_dir, table_name, duplicate_rate=0.005):
    """Write records as JSONL and add controlled cross-batch duplicates."""
    path = output_dir / f"{table_name}.jsonl"
    count = 0
    duplicate_count = 0

    with path.open("w", encoding="utf-8") as file:
        for index, original in enumerate(records):
            file.write(json.dumps(original, default=str) + "\n")
            count += 1

            if duplicate_rate and random.random() < duplicate_rate:
                duplicate = original.copy()
                duplicate["batch_id"] = "batch_002"
                duplicate["ingested_at"] = iso(
                    INGESTED_AT + timedelta(hours=6)
                )
                # The business record is unchanged, so its hash is unchanged.
                file.write(json.dumps(duplicate, default=str) + "\n")
                count += 1
                duplicate_count += 1

    print(
        f"{table_name:18} | source rows: {count - duplicate_count:>7,} "
        f"| duplicates: {duplicate_count:>5,} "
        f"| written: {count:>7,}"
    )
    return count


def generate_customers(count):
    customers = []
    for i in range(1, count + 1):
        created = random_date(date(2023, 1, 1), AS_OF - timedelta(days=30))
        employees = random.choice(
            [random.randint(2, 20), random.randint(21, 200),
             random.randint(201, 2000), random.randint(2001, 10000)]
        )
        segment = (
            "SMB" if employees <= 20
            else "Mid-Market" if employees <= 200
            else "Enterprise"
        )
        updated = random_timestamp(created, AS_OF)
        row = {
            "customer_id": f"CUST_{i:06d}",
            "company_name": fake.company(),
            "industry": random.choice(INDUSTRIES),
            "country": random.choice(COUNTRIES),
            "employee_count": employees,
            "customer_segment": segment,
            "created_at": iso(random_timestamp(created, created)),
            "updated_at": iso(updated),
        }
        customers.append(add_metadata(row, updated))
    return customers


def generate_users(customers, count):
    users = []
    customer_ids = [c["customer_id"] for c in customers]
    customer_created = {
        c["customer_id"]: datetime.fromisoformat(c["created_at"]).date()
        for c in customers
    }

    for i in range(1, count + 1):
        customer_id = random.choice(customer_ids)
        created = random_date(customer_created[customer_id], AS_OF)
        updated = random_timestamp(created, AS_OF)
        name = fake.name()
        email_name = name.lower().replace(" ", ".").replace("'", "")
        row = {
            "user_id": f"USER_{i:07d}",
            "customer_id": customer_id,
            "email": f"{email_name}.{i}@{fake.free_email_domain()}",
            "full_name": name,
            "role": random.choice(ROLES),
            "is_active": random.random() > 0.08,
            "created_at": iso(random_timestamp(created, created)),
            "updated_at": iso(updated),
        }
        users.append(add_metadata(row, updated))

    return users


def generate_plans():
    rows = []
    for plan in PLANS:
        row = {
            **plan,
            "currency": "USD",
            "is_active": True,
            "created_at": "2023-01-01T00:00:00+00:00",
            "updated_at": iso(INGESTED_AT),
        }
        rows.append(add_metadata(row, INGESTED_AT))
    return rows


def generate_subscriptions(customers, count):
    subscriptions = []
    customer_ids = [c["customer_id"] for c in customers]

    for i in range(1, count + 1):
        plan = random.choice(PLANS)
        start = random_date(date(2023, 1, 1), AS_OF - timedelta(days=15))
        status = random.choices(
            ["active", "trialing", "past_due", "canceled"],
            weights=[70, 5, 8, 17],
        )[0]

        canceled_at = None
        end_date = None
        if status == "canceled":
            end_date = random_date(start, AS_OF)
            canceled_at = iso(random_timestamp(end_date, end_date))

        period_start = max(start, AS_OF - timedelta(days=30))
        period_end = period_start + timedelta(days=30)

        updated = random_timestamp(start, AS_OF)
        row = {
            "subscription_id": f"SUB_{i:07d}",
            "customer_id": random.choice(customer_ids),
            "plan_id": plan["plan_id"],
            "status": status,
            "start_date": iso(start),
            "trial_end_date": iso(start + timedelta(days=14))
                if status == "trialing" else None,
            "current_period_start": iso(period_start),
            "current_period_end": iso(period_end),
            "cancel_at_period_end": status == "canceled" and random.random() < 0.3,
            "canceled_at": canceled_at,
            "quantity": random.randint(1, 20),
            "monthly_price": plan["monthly_price"],
            "currency": "USD",
            "created_at": iso(random_timestamp(start, start)),
            "updated_at": iso(updated),
        }
        subscriptions.append(add_metadata(row, updated))

    return subscriptions


def generate_billing(subscriptions, invoice_count):
    invoices = []
    payments = []
    subscription_by_id = {
        s["subscription_id"]: s for s in subscriptions
    }

    for i in range(1, invoice_count + 1):
        sub = random.choice(subscriptions)
        start = date.fromisoformat(sub["start_date"])
        invoice_date = random_date(start, AS_OF)
        due_date = invoice_date + timedelta(days=14)
        period_end = invoice_date
        period_start = max(start, period_end - timedelta(days=30))

        subtotal = round(float(sub["monthly_price"]) * sub["quantity"], 2)
        tax = round(subtotal * random.choice([0, 0.05, 0.10, 0.18]), 2)
        total = round(subtotal + tax, 2)
        currency = sub["currency"]

        # Most invoices have one attempt; some have a failed attempt first.
        multiple_attempts = random.random() < 0.10
        first_status = "failed" if multiple_attempts else random.choices(
            ["succeeded", "failed", "pending"],
            weights=[91, 7, 2],
        )[0]

        invoice_status = (
            "paid" if first_status == "succeeded" or multiple_attempts
            else "open" if first_status in ("failed", "pending")
            else "uncollectible"
        )
        if random.random() < 0.01:
            invoice_status = "void"

        updated = random_timestamp(invoice_date, min(AS_OF, due_date + timedelta(days=30)))
        invoice_id = f"INV_{i:07d}"

        invoice = {
            "invoice_id": invoice_id,
            "subscription_id": sub["subscription_id"],
            "invoice_number": f"NX-{i:08d}",
            "invoice_date": iso(invoice_date),
            "due_date": iso(due_date),
            "billing_period_start": iso(period_start),
            "billing_period_end": iso(period_end),
            "subtotal": subtotal,
            "tax": tax,
            "total_amount": total,
            "currency": currency,
            "status": invoice_status,
            "created_at": iso(random_timestamp(invoice_date, invoice_date)),
            "updated_at": iso(updated),
        }
        invoices.append(add_metadata(invoice, updated))

        attempt_statuses = (
            ["failed", "succeeded"] if multiple_attempts else [first_status]
        )
        for attempt, payment_status in enumerate(attempt_statuses, start=1):
            payment_time = random_timestamp(
                invoice_date, min(AS_OF, invoice_date + timedelta(days=7))
            )
            payment_updated = payment_time
            payment = {
                "payment_id": f"PAY_{i:07d}_{attempt}",
                "invoice_id": invoice_id,
                "attempt_number": attempt,
                "payment_date": iso(payment_time),
                "amount": total,
                "currency": currency,
                "payment_method": random.choice(PAYMENT_METHODS),
                "status": payment_status,
                "failure_code": (
                    random.choice(["insufficient_funds", "card_declined", "timeout"])
                    if payment_status == "failed" else None
                ),
                "created_at": iso(payment_time),
                "updated_at": iso(payment_updated),
            }
            payments.append(add_metadata(payment, payment_updated))

    return invoices, payments


def generate_product_events(users, count):
    user_customer = {
        u["user_id"]: u["customer_id"] for u in users
    }
    user_ids = list(user_customer)
    rows = []

    for i in range(1, count + 1):
        user_id = random.choice(user_ids)
        event_type, feature = random.choice(EVENTS)
        event_date = random_date(date(2024, 1, 1), AS_OF)
        event_time = random_timestamp(event_date, event_date)

        # A small proportion arrive after their event timestamp.
        ingested_at = (
            INGESTED_AT + timedelta(hours=3)
            if random.random() < 0.02 else INGESTED_AT
        )
        row = {
            "event_id": f"EVT_{i:09d}",
            "user_id": user_id,
            "customer_id": user_customer[user_id],
            "event_type": event_type,
            "feature_name": feature,
            "event_timestamp": iso(event_time),
            "event_properties": {
                "session_id": f"SESSION_{random.randint(1, 50000):06d}",
                "source": random.choice(["web", "mobile", "api"]),
                "duration_seconds": random.randint(1, 1800),
            },
        }
        row = add_metadata(row, event_time)
        row["ingested_at"] = iso(ingested_at)

        # Intentionally introduce a tiny number of invalid foreign keys.
        if i % 5000 == 0:
            row["user_id"] = "USER_DOES_NOT_EXIST"
            row["record_hash"] = record_hash(row)

        rows.append(row)

    return rows


def generate_support_tickets(customers, users, count):
    users_by_customer = {}
    for user in users:
        users_by_customer.setdefault(user["customer_id"], []).append(user)

    rows = []
    for i in range(1, count + 1):
        customer_id = random.choice(customers)["customer_id"]
        customer_users = users_by_customer.get(customer_id, [])
        user_id = (
            random.choice(customer_users)["user_id"]
            if customer_users and random.random() > 0.05 else None
        )

        created_date = random_date(date(2024, 1, 1), AS_OF)
        created_at = random_timestamp(created_date, created_date)
        status = random.choices(
            ["open", "in_progress", "resolved", "closed"],
            weights=[15, 20, 35, 30],
        )[0]

        first_response = (
            created_at + timedelta(hours=random.randint(1, 48))
            if status != "open" else None
        )
        resolved_at = (
            first_response + timedelta(hours=random.randint(1, 120))
            if status in ("resolved", "closed") else None
        )
        updated = resolved_at or first_response or created_at

        row = {
            "ticket_id": f"TICKET_{i:07d}",
            "customer_id": customer_id,
            "user_id": user_id,
            "subject": fake.sentence(nb_words=6),
            "category": random.choice(TICKET_CATEGORIES),
            "priority": random.choice(["low", "medium", "high", "urgent"]),
            "status": status,
            "created_at": iso(created_at),
            "first_response_at": iso(first_response) if first_response else None,
            "resolved_at": iso(resolved_at) if resolved_at else None,
            "updated_at": iso(updated),
        }
        rows.append(add_metadata(row, updated))

    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Generate NexusFlow synthetic SaaS source data."
    )
    parser.add_argument("--customers", type=int, default=5000)
    parser.add_argument("--users", type=int, default=20000)
    parser.add_argument("--subscriptions", type=int, default=7000)
    parser.add_argument("--invoices", type=int, default=30000)
    parser.add_argument("--events", type=int, default=200000)
    parser.add_argument("--tickets", type=int, default=10000)
    parser.add_argument("--output-dir", default="data/generated")
    parser.add_argument("--no-duplicates", action="store_true")
    args = parser.parse_args()

    random.seed(SEED)
    Faker.seed(SEED)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    duplicate_rate = 0 if args.no_duplicates else 0.005

    print("Generating NexusFlow source data...")
    print(f"Output directory: {output_dir.resolve()}")
    print(f"Random seed: {SEED}")
    print("-" * 78)

    customers = generate_customers(args.customers)
    users = generate_users(customers, args.users)
    plans = generate_plans()
    subscriptions = generate_subscriptions(customers, args.subscriptions)
    invoices, payments = generate_billing(subscriptions, args.invoices)
    events = generate_product_events(users, args.events)
    tickets = generate_support_tickets(customers, users, args.tickets)

    tables = [
        ("customers", customers),
        ("users", users),
        ("plans", plans),
        ("subscriptions", subscriptions),
        ("invoices", invoices),
        ("payments", payments),
        ("product_events", events),
        ("support_tickets", tickets),
    ]

    total_written = 0
    for table_name, records in tables:
        total_written += write_jsonl(
            records, output_dir, table_name, duplicate_rate
        )

    print("-" * 78)
    print(f"Total rows written, including duplicates: {total_written:,}")
    print("Generation complete.")


if __name__ == "__main__":
    main()