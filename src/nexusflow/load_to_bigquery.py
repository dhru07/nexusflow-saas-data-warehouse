from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List

from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPICallError


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

PROJECT_ID = "data-engineering-course-511511"
DATASET_ID = "saas_raw"
LOCATION = "asia-south2"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "generated"

METADATA_FIELDS = [
    bigquery.SchemaField("batch_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("source_updated_at", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("record_hash", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("is_deleted", "BOOL", mode="NULLABLE"),
]


# ---------------------------------------------------------------------------
# BIGQUERY SCHEMAS
# ---------------------------------------------------------------------------
# These schemas describe the expected source fields plus ingestion metadata.
# BigQuery will not infer types from the JSONL files.

TABLE_SCHEMAS: Dict[str, List[bigquery.SchemaField]] = {

    "customers": [
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("company_name", "STRING"),
        bigquery.SchemaField("industry", "STRING"),
        bigquery.SchemaField("country", "STRING"),
        bigquery.SchemaField("employee_count", "INT64"),
        bigquery.SchemaField("customer_segment", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        *METADATA_FIELDS,
    ],

    "users": [
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("email", "STRING"),
        bigquery.SchemaField("full_name", "STRING"),
        bigquery.SchemaField("role", "STRING"),
        bigquery.SchemaField("is_active", "BOOL"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        *METADATA_FIELDS,
    ],

    "plans": [
        bigquery.SchemaField("plan_id", "STRING"),
        bigquery.SchemaField("plan_name", "STRING"),
        bigquery.SchemaField("monthly_price", "NUMERIC"),
        bigquery.SchemaField("billing_interval", "STRING"),
        bigquery.SchemaField("max_users", "INT64"),
        bigquery.SchemaField("is_active", "BOOL"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        bigquery.SchemaField("currency", "STRING"),
        *METADATA_FIELDS,
    ],

    "subscriptions": [
        bigquery.SchemaField("subscription_id", "STRING"),
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("plan_id", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("start_date", "DATE"),
        bigquery.SchemaField("trial_end_date", "DATE"),
        bigquery.SchemaField("current_period_start", "DATE"),
        bigquery.SchemaField("current_period_end", "DATE"),
        bigquery.SchemaField("cancel_at_period_end", "BOOL"),
        bigquery.SchemaField("canceled_at", "TIMESTAMP"),
        bigquery.SchemaField("quantity", "INT64"),
        bigquery.SchemaField("monthly_price", "NUMERIC"),
        bigquery.SchemaField("currency", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        *METADATA_FIELDS,
    ],

    "invoices": [
        bigquery.SchemaField("invoice_id", "STRING"),
        bigquery.SchemaField("subscription_id", "STRING"),
        bigquery.SchemaField("invoice_number", "STRING"),
        bigquery.SchemaField("invoice_date", "DATE"),
        bigquery.SchemaField("due_date", "DATE"),
        bigquery.SchemaField("billing_period_start", "DATE"),
        bigquery.SchemaField("billing_period_end", "DATE"),
        bigquery.SchemaField("subtotal", "NUMERIC"),
        bigquery.SchemaField("tax", "NUMERIC"),
        bigquery.SchemaField("total_amount", "NUMERIC"),
        bigquery.SchemaField("currency", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        *METADATA_FIELDS,
    ],

    "payments": [
        bigquery.SchemaField("payment_id", "STRING"),
        bigquery.SchemaField("invoice_id", "STRING"),
        bigquery.SchemaField("attempt_number", "INT64"),
        bigquery.SchemaField("payment_date", "TIMESTAMP"),
        bigquery.SchemaField("amount", "NUMERIC"),
        bigquery.SchemaField("currency", "STRING"),
        bigquery.SchemaField("payment_method", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("failure_code", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        *METADATA_FIELDS,
    ],

    "product_events": [
        bigquery.SchemaField("event_id", "STRING"),
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("event_type", "STRING"),
        bigquery.SchemaField("feature_name", "STRING"),
        bigquery.SchemaField("event_timestamp", "TIMESTAMP"),
        bigquery.SchemaField("event_properties", "JSON"),
        *METADATA_FIELDS,
    ],

    "support_tickets": [
        bigquery.SchemaField("ticket_id", "STRING"),
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("subject", "STRING"),
        bigquery.SchemaField("category", "STRING"),
        bigquery.SchemaField("priority", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("first_response_at", "TIMESTAMP"),
        bigquery.SchemaField("resolved_at", "TIMESTAMP"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
        *METADATA_FIELDS,
    ],
}


# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ---------------------------------------------------------------------------
# FILE VALIDATION
# ---------------------------------------------------------------------------

def count_jsonl_rows(file_path: Path) -> int:
    """Count non-empty JSONL records without loading the entire file."""

    with file_path.open("r", encoding="utf-8") as file:
        return sum(1 for line in file if line.strip())


def validate_input_files(
    data_dir: Path,
    selected_tables: List[str],
) -> Dict[str, Path]:
    """Verify all requested JSONL files exist before starting any load."""

    files = {}

    for table_name in selected_tables:
        file_path = data_dir / f"{table_name}.jsonl"

        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing source file for table '{table_name}': {file_path}"
            )

        if file_path.stat().st_size == 0:
            raise ValueError(
                f"Source file is empty: {file_path}"
            )

        files[table_name] = file_path

    return files


# ---------------------------------------------------------------------------
# BIGQUERY CLIENT AND DATASET VALIDATION
# ---------------------------------------------------------------------------

def create_bigquery_client(
    project_id: str,
    location: str,
) -> bigquery.Client:
    """
    Create a BigQuery client using Application Default Credentials.

    Authentication is provided by:
        gcloud auth application-default login

    No service-account key or token is stored in this project.
    """

    logging.info("Creating BigQuery client...")
    logging.info("GCP project: %s", project_id)
    logging.info("BigQuery location: %s", location)

    client = bigquery.Client(
        project=project_id,
        location=location,
    )

    logging.info("BigQuery client created successfully.")

    return client


def validate_dataset(
    client: bigquery.Client,
    dataset_id: str,
    location: str,
) -> None:
    """Confirm the target dataset exists and is in the expected region."""

    dataset_ref = f"{client.project}.{dataset_id}"

    logging.info("Checking target dataset: %s", dataset_ref)

    dataset = client.get_dataset(dataset_ref)

    actual_location = dataset.location.lower()
    expected_location = location.lower()

    if actual_location != expected_location:
        raise ValueError(
            f"Dataset location mismatch. "
            f"Expected '{expected_location}', "
            f"found '{actual_location}'."
        )

    logging.info(
        "Dataset validated: %s (%s)",
        dataset_ref,
        dataset.location,
    )


# ---------------------------------------------------------------------------
# LOAD JOB CONFIGURATION
# ---------------------------------------------------------------------------

def build_load_config(
    schema: List[bigquery.SchemaField],
    write_disposition: str,
) -> bigquery.LoadJobConfig:
    """Build an explicit newline-delimited JSON load configuration."""

    return bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=schema,
        autodetect=False,
        write_disposition=write_disposition,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
        max_bad_records=0,
        ignore_unknown_values=False,
    )


# ---------------------------------------------------------------------------
# LOAD ONE TABLE
# ---------------------------------------------------------------------------

def load_table(
    client: bigquery.Client,
    table_name: str,
    file_path: Path,
    dataset_id: str,
    location: str,
    write_disposition: str,
) -> Dict[str, object]:
    """
    Load one JSONL file into BigQuery.

    Returns a summary containing:
        table name
        expected local rows
        loaded BigQuery rows
        BigQuery job ID
        destination table
    """

    if table_name not in TABLE_SCHEMAS:
        raise ValueError(f"No schema defined for table: {table_name}")

    destination = f"{client.project}.{dataset_id}.{table_name}"

    expected_rows = count_jsonl_rows(file_path)

    logging.info("-" * 72)
    logging.info("Starting load for: %s", table_name)
    logging.info("Source file: %s", file_path)
    logging.info("File size: %.2f MB", file_path.stat().st_size / (1024 * 1024))
    logging.info("Expected rows: %s", f"{expected_rows:,}")
    logging.info("Destination: %s", destination)
    logging.info("Write disposition: %s", write_disposition)

    job_config = build_load_config(
        schema=TABLE_SCHEMAS[table_name],
        write_disposition=write_disposition,
    )

    try:
        with file_path.open("rb") as source_file:
            load_job = client.load_table_from_file(
                source_file,
                destination,
                job_config=job_config,
                location=location,
            )

            logging.info(
                "Submitted BigQuery load job: %s",
                load_job.job_id,
            )

            load_job.result()

        if load_job.errors:
            raise RuntimeError(
                f"BigQuery reported errors for {table_name}: "
                f"{load_job.errors}"
            )

        table = client.get_table(destination)
        loaded_rows = table.num_rows

        logging.info("Load job completed.")
        logging.info("BigQuery rows: %s", f"{loaded_rows:,}")

        if write_disposition == bigquery.WriteDisposition.WRITE_TRUNCATE:
            if loaded_rows != expected_rows:
                raise RuntimeError(
                    f"Row-count mismatch for {table_name}. "
                    f"Local file has {expected_rows:,} rows, "
                    f"BigQuery table has {loaded_rows:,} rows."
                )

        logging.info("[PASS] %s loaded successfully.", table_name)

        return {
            "table": table_name,
            "destination": destination,
            "expected_rows": expected_rows,
            "loaded_rows": loaded_rows,
            "job_id": load_job.job_id,
            "status": "SUCCESS",
        }

    except Exception:
        logging.exception("Failed to load table: %s", table_name)
        raise


# ---------------------------------------------------------------------------
# LOAD ALL TABLES
# ---------------------------------------------------------------------------

def load_all_tables(
    client: bigquery.Client,
    data_dir: Path,
    dataset_id: str,
    location: str,
    selected_tables: List[str],
    write_disposition: str,
) -> List[Dict[str, object]]:
    """Load the requested source tables sequentially."""

    input_files = validate_input_files(
        data_dir=data_dir,
        selected_tables=selected_tables,
    )

    validate_dataset(
        client=client,
        dataset_id=dataset_id,
        location=location,
    )

    results = []

    logging.info("=" * 72)
    logging.info("NEXUSFLOW BIGQUERY INGESTION")
    logging.info("=" * 72)
    logging.info("Tables to load: %s", len(selected_tables))
    logging.info("Target dataset: %s.%s", client.project, dataset_id)
    logging.info("Write disposition: %s", write_disposition)

    for table_name in selected_tables:
        result = load_table(
            client=client,
            table_name=table_name,
            file_path=input_files[table_name],
            dataset_id=dataset_id,
            location=location,
            write_disposition=write_disposition,
        )

        results.append(result)

    return results


# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------

def print_summary(results: List[Dict[str, object]]) -> None:
    """Print a readable ingestion summary."""

    print("\n")
    print("=" * 88)
    print("NEXUSFLOW INGESTION SUMMARY")
    print("=" * 88)

    print(
        f"{'TABLE':20} "
        f"{'LOCAL ROWS':>14} "
        f"{'BQ ROWS':>14} "
        f"{'STATUS':>14}"
    )

    print("-" * 88)

    total_local = 0
    total_loaded = 0

    for result in results:
        local_rows = int(result["expected_rows"])
        loaded_rows = int(result["loaded_rows"])

        total_local += local_rows
        total_loaded += loaded_rows

        print(
            f"{str(result['table']):20} "
            f"{local_rows:14,} "
            f"{loaded_rows:14,} "
            f"{str(result['status']):>14}"
        )

    print("-" * 88)

    print(
        f"{'TOTAL':20} "
        f"{total_local:14,} "
        f"{total_loaded:14,}"
    )

    print("=" * 88)

    print("\nBigQuery load jobs:")

    for result in results:
        print(
            f"  {result['table']}: "
            f"{result['job_id']}"
        )

    print("\nAll requested tables loaded successfully.")


# ---------------------------------------------------------------------------
# COMMAND-LINE ARGUMENTS
# ---------------------------------------------------------------------------

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load NexusFlow synthetic source data into BigQuery."
    )

    parser.add_argument(
        "--project",
        default=PROJECT_ID,
        help="Google Cloud project ID.",
    )

    parser.add_argument(
        "--dataset",
        default=DATASET_ID,
        help="Destination BigQuery dataset.",
    )

    parser.add_argument(
        "--location",
        default=LOCATION,
        help="BigQuery dataset location.",
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory containing JSONL source files.",
    )

    parser.add_argument(
        "--tables",
        default=",".join(TABLE_SCHEMAS.keys()),
        help=(
            "Comma-separated table names. "
            "Defaults to all eight source tables."
        ),
    )

    parser.add_argument(
        "--write-disposition",
        choices=[
            "WRITE_TRUNCATE",
            "WRITE_APPEND",
            "WRITE_EMPTY",
        ],
        default="WRITE_TRUNCATE",
        help=(
            "BigQuery write behavior. "
            "Default is WRITE_TRUNCATE for repeatable initial loads."
        ),
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main() -> int:
    configure_logging()

    args = parse_arguments()

    selected_tables = [
        table.strip()
        for table in args.tables.split(",")
        if table.strip()
    ]

    unknown_tables = [
        table
        for table in selected_tables
        if table not in TABLE_SCHEMAS
    ]

    if unknown_tables:
        logging.error(
            "Unknown table names: %s",
            ", ".join(unknown_tables),
        )
        return 1

    if not selected_tables:
        logging.error("No tables were selected.")
        return 1

    try:
        client = create_bigquery_client(
            project_id=args.project,
            location=args.location,
        )

        results = load_all_tables(
            client=client,
            data_dir=args.data_dir,
            dataset_id=args.dataset,
            location=args.location,
            selected_tables=selected_tables,
            write_disposition=args.write_disposition,
        )

        print_summary(results)

        return 0

    except FileNotFoundError as exc:
        logging.error("Input file error: %s", exc)
        return 1

    except ValueError as exc:
        logging.error("Configuration or validation error: %s", exc)
        return 1

    except GoogleAPICallError:
        logging.exception("Google Cloud API error during ingestion.")
        return 1

    except Exception:
        logging.exception("Unexpected ingestion failure.")
        return 1


if __name__ == "__main__":
    sys.exit(main())