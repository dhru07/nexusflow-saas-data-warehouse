# BigQuery Performance Analysis — NexusFlow

**Project:** `data-engineering-course-511511`
**Region:** `asia-south2`
**Dataset:** `saas_marts` and supporting intermediate/raw views
**Benchmark date:** 6 November 2026

## 1. Scope

This report records observed BigQuery execution statistics for representative product-usage and monthly recurring revenue (MRR) queries. It distinguishes bytes processed from bytes billed and avoids attributing improvements to clustering where the benchmark does not isolate that effect.

## 2. Product-usage table design

The Gold fact table `saas_marts.fact_product_usage` contains **200,460 rows** and is configured with:

- **Partitioning:** daily partitioning on `event_date`
- **Clustering:** `customer_id`, `user_id`
- **Logical storage:** 27,329,175 bytes (about 26.1 MiB)
- **Physical storage:** 8,260,533 bytes (about 7.88 MiB)

These properties were verified from the BigQuery table metadata.

## 3. Query execution results

| Workload | Bytes processed | Bytes billed | Partitions processed | Slot-ms | Execution duration |
|---|---:|---:|---:|---:|---:|
| Full product-usage scan | 6,146,974 | 10 MiB | 1,041 | 26,535 | 150 ms |
| Date-partition-filtered aggregation | 237,530 | 10 MiB | 31 | 400 | 19 ms |
| Date + customer filter (`CUST_004944`) | 402,838 | 10 MiB | 31 | 162 | 17 ms |
| Monthly MRR aggregation | 588,279 | 10 MiB | 0 | 25 | 20 ms |

All four query jobs reported `cacheHit = false`.

**Metric definitions:** bytes processed is the amount of data scanned by the query; bytes billed is the amount used for billing. The observed 10 MiB billed amount for each query reflects BigQuery's minimum billing quantum, so it should not be confused with bytes processed. Execution duration is the BigQuery job's `finalExecutionDurationMs`; timings are single-run observations, not a repeated controlled benchmark.

## 4. Partition-pruning analysis

The full scan processed 6,146,974 bytes across 1,041 partitions. The date-filtered query processed 237,530 bytes across 31 partitions.

- **Bytes processed reduction:** 96.13%
- **Partition count reduction:** 97.02% (1,041 to 31)
- **Slot-ms reduction:** 98.49% (26,535 to 400)

This is direct evidence that filtering on the partitioning column `event_date` prunes partitions and reduces the amount of data processed for this workload.

The date-filtered query returned 10 event-type groups and read 6,171 records in its query plan.

## 5. Customer-filter / clustering analysis

The customer-filter query used:

```sql
SELECT
    customer_id,
    user_id,
    event_type,
    event_timestamp,
    feature_name
FROM `data-engineering-course-511511.saas_marts.fact_product_usage`
WHERE event_date >= DATE '2026-10-01'
  AND event_date < DATE '2026-11-01'
  AND customer_id = 'CUST_004944'
LIMIT 1000;
```

Observed execution:

- Bytes processed: 402,838
- Bytes billed: 10 MiB
- Partitions processed: 31
- Slot-ms: 162
- Execution duration: 17 ms
- Records read in the query plan: 5,578

The query includes both a partition predicate and a clustered-column predicate. However, it is not directly comparable to the date-only query: it selects individual columns and applies `LIMIT 1000`, while the date-only query groups and aggregates events. Therefore, this run confirms the combined filter executes, but **does not isolate or prove a clustering-related reduction**. A controlled clustering benchmark would need equivalent projections, predicates, result logic, and data layout, with comparisons across representative customer filters.

## 6. Monthly MRR query

The representative MRR query aggregated current MRR and customer counts by currency from `saas_intermediate.int_monthly_recurring_revenue`.

Observed execution:

- Bytes processed: 588,279
- Bytes billed: 10 MiB
- Slot-ms: 25
- Execution duration: 20 ms
- Query plan records read: 7,037

The query plan shows that the logical view chain reads from the raw `subscriptions` table and applies the source deduplication/current-subscription logic. The measured 588,279 bytes is the observed scan for this execution, not a benchmark against an alternative MRR implementation.

## 7. Interpretation and limitations

1. Partition pruning is the strongest demonstrated optimization in this benchmark: the date-filtered query processed 96.13% fewer bytes than the full scan.
2. The fact table's daily partitioning and customer/user clustering are configured and verified in table metadata.
3. The customer-filter query is a useful representative access pattern, but the current comparison does not isolate the incremental effect of clustering.
4. Each query was billed at 10 MiB. For this relatively small table, billed bytes do not show the same percentage reduction as processed bytes.
5. Execution durations are single observations on a small synthetic dataset. They should not be presented as stable production latency or generalized without repeated runs and larger data volumes.
6. The MRR query is a representative BI workload; its observed statistics do not by themselves establish a before/after performance gain.

## 8. Conclusion

The NexusFlow Gold product-usage fact table uses daily date partitioning and clustering by customer and user. The measured date-filtered workload demonstrates substantial partition pruning: 96.13% fewer bytes processed and 98.49% fewer slot-ms than the full-scan workload. A customer-filtered workload and monthly MRR workload were also executed and measured. Further controlled testing is required before quantifying a separate clustering benefit.
