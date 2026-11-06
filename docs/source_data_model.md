# NexusFlow — Source Data Model

## 1. Business Context

NexusFlow is a fictional B2B SaaS company that provides subscription-based
software to business customers.

The warehouse will support analytics across:

- Customer acquisition and growth
- Subscription lifecycle and recurring revenue
- Invoicing and payment performance
- Product engagement and feature adoption
- Customer support and service quality

## 2. Source Tables and Expected Volumes

| Source table | Expected records | Grain |
|---|---:|---|
| customers | 5,000 | One row per company |
| users | 20,000 | One row per user |
| plans | 5 | One row per pricing plan |
| subscriptions | 7,000 | One row per subscription |
| invoices | 30,000 | One row per invoice |
| payments | 30,000 | One row per payment attempt |
| product_events | 200,000 | One row per product event |
| support_tickets | 10,000 | One row per support ticket |

These are generation targets, not measured output counts.

## 3. Table Schemas

### 3.1 customers

Grain: One record per business customer.

| Column | BigQuery type | Description |
|---|---|---|
| customer_id | STRING | Primary identifier |
| company_name | STRING | Company name |
| industry | STRING | Customer industry |
| country | STRING | Customer country |
| employee_count | INT64 | Approximate company size |
| customer_segment | STRING | SMB, Mid-Market or Enterprise |
| created_at | TIMESTAMP | Customer creation time |
| updated_at | TIMESTAMP | Last source update |

### 3.2 users

Grain: One record per user belonging to a customer.

| Column | BigQuery type | Description |
|---|---|---|
| user_id | STRING | Primary identifier |
| customer_id | STRING | Owning customer |
| email | STRING | User email |
| full_name | STRING | User full name |
| role | STRING | User role |
| is_active | BOOL | Whether the user is active |
| created_at | TIMESTAMP | User creation time |
| updated_at | TIMESTAMP | Last source update |

### 3.3 plans

Grain: One record per pricing plan.

| Column | BigQuery type | Description |
|---|---|---|
| plan_id | STRING | Primary identifier |
| plan_name | STRING | Pricing plan name |
| monthly_price | NUMERIC | Monthly list price |
| billing_interval | STRING | Monthly or annual |
| max_users | INT64 | User limit, nullable for unlimited |
| is_active | BOOL | Whether the plan is offered |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last source update |

### 3.4 subscriptions

Grain: One record per subscription.

| Column | BigQuery type | Description |
|---|---|---|
| subscription_id | STRING | Primary identifier |
| customer_id | STRING | Subscribing customer |
| plan_id | STRING | Selected pricing plan |
| status | STRING | trialing, active, past_due or canceled |
| start_date | DATE | Subscription start date |
| trial_end_date | DATE | Trial end date, nullable |
| current_period_start | DATE | Current billing period start |
| current_period_end | DATE | Current billing period end |
| cancel_at_period_end | BOOL | Whether cancellation is scheduled |
| canceled_at | TIMESTAMP | Actual cancellation time, nullable |
| quantity | INT64 | Number of licensed units |
| monthly_price | NUMERIC | Agreed monthly-equivalent price |
| currency | STRING | Currency code |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last source update |

### 3.5 invoices

Grain: One record per invoice.

| Column | BigQuery type | Description |
|---|---|---|
| invoice_id | STRING | Primary identifier |
| subscription_id | STRING | Related subscription |
| invoice_number | STRING | Human-readable invoice number |
| invoice_date | DATE | Invoice issue date |
| due_date | DATE | Payment due date |
| billing_period_start | DATE | Billing period start |
| billing_period_end | DATE | Billing period end |
| subtotal | NUMERIC | Amount before tax |
| tax | NUMERIC | Tax amount |
| total_amount | NUMERIC | Total invoice amount |
| currency | STRING | Currency code |
| status | STRING | draft, open, paid, void or uncollectible |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last source update |

### 3.6 payments

Grain: One record per payment attempt.

| Column | BigQuery type | Description |
|---|---|---|
| payment_id | STRING | Primary identifier |
| invoice_id | STRING | Related invoice |
| attempt_number | INT64 | Attempt sequence for invoice |
| payment_date | TIMESTAMP | Attempt time, nullable |
| amount | NUMERIC | Attempted payment amount |
| currency | STRING | Currency code |
| payment_method | STRING | Payment method |
| status | STRING | succeeded, failed, pending or refunded |
| failure_code | STRING | Failure reason, nullable |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last source update |

### 3.7 product_events

Grain: One record per user product interaction.

| Column | BigQuery type | Description |
|---|---|---|
| event_id | STRING | Primary identifier |
| user_id | STRING | User who generated the event |
| customer_id | STRING | Associated customer |
| event_type | STRING | Event category |
| feature_name | STRING | Product feature used |
| event_timestamp | TIMESTAMP | Time of user activity |
| event_properties | JSON | Additional event attributes |

### 3.8 support_tickets

Grain: One record per support ticket.

| Column | BigQuery type | Description |
|---|---|---|
| ticket_id | STRING | Primary identifier |
| customer_id | STRING | Related customer |
| user_id | STRING | Ticket creator, nullable |
| subject | STRING | Ticket subject |
| category | STRING | Support category |
| priority | STRING | low, medium, high or urgent |
| status | STRING | open, in_progress, resolved or closed |
| created_at | TIMESTAMP | Creation time |
| first_response_at | TIMESTAMP | First response time, nullable |
| resolved_at | TIMESTAMP | Resolution time, nullable |
| updated_at | TIMESTAMP | Last source update |

## 4. Common Ingestion Metadata

Every raw table will include:

| Column | BigQuery type | Purpose |
|---|---|---|
| batch_id | STRING | Identifies ingestion batch |
| ingested_at | TIMESTAMP | Time the warehouse received the record |
| source_updated_at | TIMESTAMP | Source record's last update time |
| record_hash | STRING | Hash of business fields for change detection |
| is_deleted | BOOL | Soft-delete indicator |

The record hash will exclude ingestion metadata so that the same business record
does not appear changed merely because it was ingested again.

## 5. Entity Relationships

- One customer can have multiple users.
- One customer can have multiple subscriptions over time.
- Each subscription references one pricing plan.
- One subscription can generate multiple invoices.
- One invoice can have multiple payment attempts.
- One user can generate multiple product events.
- One customer can have multiple support tickets.
- A support ticket may optionally reference a user.

These are logical relationships and will be validated through dbt tests.

## 6. Data Engineering Scenarios

The synthetic source data will deliberately include:

1. Multiple ingestion batches.
2. Duplicate records across batches.
3. Late-arriving product events.
4. Invalid records and missing foreign keys.
5. Customer attribute changes.
6. Subscription upgrades and downgrades.
7. Subscription renewals and cancellations.
8. Multiple payment attempts for an invoice.
9. Soft-deleted records.

## 7. Warehouse Layers

| Layer | BigQuery dataset | Responsibility |
|---|---|---|
| Raw | saas_raw | Source records and ingestion metadata |
| Staging | saas_staging | Standardization and deduplication |
| Intermediate | saas_intermediate | Business logic and reusable transformations |
| Marts | saas_marts | Analytics-ready facts and dimensions |

## 8. Planned Analytics

The final warehouse should support:

- Monthly Recurring Revenue (MRR)
- Annual Recurring Revenue (ARR)
- Customer growth
- Subscription churn
- Renewal and cancellation trends
- Upgrade and downgrade analysis
- Payment success rate
- Product feature adoption
- Daily and monthly active users
- Support ticket resolution time

Revenue calculations will use subscription lifecycle and billing rules rather
than simply summing invoice or payment amounts.
