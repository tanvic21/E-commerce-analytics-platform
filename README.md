# E-Commerce Analytics Platform

## Project Overview

The **E-Commerce Analytics Platform** is a production-style data analytics project demonstrating an end-to-end workflow from raw e-commerce data to business insights.

It combines:

- Data cleaning and validation
- SQL-based analytics
- Python-based incremental processing
- SQLite database storage
- Data-quality and rejected-record handling
- Watermark-based incremental loading
- Insert/update upsert processing
- Pipeline execution monitoring
- Power BI dashboarding
- Business KPI analysis

The project simulates a realistic e-commerce environment where new and changed records arrive continuously and should be processed without reprocessing the entire dataset.

---

## Business Objective

The business wants to understand:

- Revenue and order performance
- Average Order Value (AOV)
- Profitability
- Product and category performance
- Customer segment performance
- Returns and refunds
- Payment performance
- Monthly trends
- Customer behavior
- Marketing performance
- Reasons for changes in revenue and profit

A key business investigation is:

> **Revenue increased, but profit decreased. Why?**

Possible causes include higher returns, increased discounts, increased product costs, refunds, or operational costs.

---

## Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Data Processing | Pandas |
| Database | SQLite |
| Querying | SQL |
| Visualization | Power BI |
| Version Control | Git |
| Data Source | CSV |
| Incremental Processing | Watermark-based ingestion |

---

## Dataset

Core datasets:

1. Customers
2. Orders
3. Order Items
4. Products
5. Payments
6. Returns
7. Marketing Campaigns

### Initial Dataset Sizes

| Table | Raw Records |
|---|---:|
| Customers | 6,001 |
| Orders | 20,001 |
| Products | 501 |
| Order Items | 40,001 |
| Payments | 19,990 |
| Returns | 3,001 |

The raw datasets intentionally contain data-quality issues to simulate real-world data.

---

# Data Quality & Cleaning

Typical issues included:

- Duplicate records
- Missing values
- Invalid IDs
- Invalid categories/statuses
- Negative quantities
- Negative prices
- Invalid dates
- Future dates
- Invalid foreign keys
- Invalid payment statuses
- Invalid return reasons
- Excessive discounts
- Conflicting duplicate records

### Cleaning Principles

1. Preserve valid records.
2. Reject records that violate defined rules.
3. Store rejected records separately for investigation.
4. Validate referential integrity.
5. Run post-cleaning validation.

### Final Clean Dataset Sizes

| Table | Clean Records |
|---|---:|
| Customers | 5,998 |
| Orders | 19,989 |
| Products | 493 |
| Order Items | 39,992 |
| Payments | 19,982 |
| Returns | 2,991 |

---

# Data Model

```text
Customers
    │
    │ 1 : *
    ▼
Orders
    │
    ├────────────── 1 : * ──────────────► Order Items
    │                                      │
    │                                      │ * : 1
    │                                      ▼
    │                                   Products
    │
    └────────────── 1 : * ──────────────► Returns

Payments
    │
    └── Disconnected analytical table

Calendar
    │
    └──────────── 1 : * ──────────────► Orders
```

---

# Key Business Metrics

### Revenue

```text
Revenue = (Quantity × Unit Price) − Discount
```

### Cost

```text
Cost = Quantity × Unit Cost
```

### Profit

```text
Profit = Revenue − Cost
```

### Average Order Value

```text
AOV = Revenue / Number of Orders
```

### Return Rate

```text
Return Rate = Returned Orders / Total Orders
```

---

# SQL Analytics

Core SQL analysis includes:

- Total Revenue
- Total Orders
- Average Order Value
- Total Profit

Additional interview-oriented analysis includes:

- Monthly Revenue and Profit
- Top Products
- Category Performance
- Customer Segment Performance
- Return Rate
- Payment Success Rate

---

# Power BI Dashboard

The dashboard provides an executive-level view of the e-commerce business.

### KPI Cards

- Total Revenue
- Total Orders
- AOV
- Total Profit
- Return Rate
- Total Refund Amount
- Payment Success Rate

### Filters

- Date
- Category
- Customer Segment

### Charts

- Monthly Revenue & Profit Trend
- Category Performance
- Top 10 Products by Revenue
- Customer Segment Performance
- Return Reasons
- Payment Performance

The dashboard uses a consistent business-oriented design with KPI cards, filters, trend analysis, product/category analysis, customer analysis, and operational metrics.

---

# Phase 10 — Incremental Data Pipeline

The project implements a production-style incremental pipeline using Python and SQLite.

## Why Incremental Processing?

A real production system should not process the complete dataset every time new data arrives.

The pipeline stores the latest successfully processed `modified_at` timestamp.

A record is processed when:

```text
modified_at > last_successful_watermark
```

---

# Incremental Pipeline Architecture

```text
                    CSV Source
                        │
                        ▼
                 pipeline.py
                        │
                        ▼
              Incremental Extract
                        │
                 Watermark Check
                        │
                        ▼
                  Staging Table
                 orders_staging
                        │
                        ▼
                Data Validation
                   /        \
                  /          \
             Valid            Rejected
               │                 │
               │                 ▼
               │          rejected_orders
               │
               ▼
             Upsert
          /            \
     New Order       Existing Order
        │                 │
      INSERT            UPDATE
        \                 /
         \               /
          ▼             ▼
             orders
                │
                ▼
        Update Watermark
                │
                ▼
        Pipeline Run Log
                │
                ▼
        Staging Cleanup
```

---

# Pipeline Components

| File | Responsibility |
|---|---|
| `pipeline.py` | Orchestrates the complete pipeline |
| `incremental_extract.py` | Extracts records newer than the watermark |
| `stage_incremental.py` | Loads incremental records into staging |
| `validate_incremental.py` | Validates incoming records |
| `save_rejected.py` | Saves rejected records |
| `upsert_orders.py` | Inserts new records and updates existing records |
| `update_watermark.py` | Updates the successful processing watermark |
| `cleanup_staging.py` | Clears temporary staging records |
| `pipeline_runs.py` | Creates pipeline execution history |
| `add_run_id_to_counts.py` | Tracks insert/update counts |
| `check_database.py` | Verifies database contents |
| `verify_upsert.py` | Verifies inserted/updated records |

---

# Pipeline Control Tables

## `pipeline_control`

Stores the current pipeline state:

- `pipeline_name`
- `last_successful_watermark`
- `last_run_time`
- `status`
- `records_processed`

Example:

```text
orders_pipeline
SUCCESS
2026-10-03 11:45:00
```

## `pipeline_runs`

Stores execution history:

- Run ID
- Pipeline name
- Start time
- End time
- Status
- Records extracted
- Records valid
- Records rejected
- Records inserted
- Records updated
- Watermark

Example:

```text
Run ID:       3
Status:       SUCCESS
Extracted:    4
Valid:        3
Rejected:     1
Inserted:     2
Updated:      1
Watermark:    2026-10-03 11:45:00
```

---

# Incremental Processing Example

A sample incremental batch contained:

```text
O020010  → New
O020011  → New
O005001  → Existing order update
O020012  → Invalid customer
```

Processing result:

```text
Extracted : 4
Valid     : 3
Rejected  : 1
Inserted  : 2
Updated   : 1
```

The invalid customer record was rejected and stored separately.

The existing order was updated rather than duplicated.

---

# Reprocessing / Idempotency Check

The same already-processed batch was executed again.

Because the watermark had already advanced:

```text
Records extracted: 0
```

The pipeline safely produced:

```text
Inserted: 0
Updated: 0
Rejected: 0
```

This demonstrates safe repeated execution for already-processed input.

---

# Failure Handling

The pipeline was tested with an invalid source file.

It correctly:

- Created a new Run ID
- Detected the failure
- Marked the run as `FAILED`
- Preserved the previous successful watermark
- Did not perform a new successful upsert

---

# Staging Cleanup

After successful processing, the temporary staging table is cleared.

Final verification:

```text
orders_staging records = 0
```

This prevents old staging records from affecting later runs.

---

# Project Structure

```text
E-Commerce Analytics Platform/
│
├── clean data/
│   ├── customers_clean.csv
│   ├── orders_clean.csv
│   ├── products_clean.csv
│   ├── order_items_clean.csv
│   ├── payments_clean.csv
│   └── returns_clean.csv
│
├── Pipeline/
│   ├── initial_load.py
│   ├── check_database.py
│   ├── add_modified_at.py
│   ├── create_control_table.py
│   ├── incremental_extract.py
│   ├── stage_incremental.py
│   ├── validate_incremental.py
│   ├── save_rejected.py
│   ├── upsert_orders.py
│   ├── verify_upsert.py
│   ├── update_watermark.py
│   ├── pipeline.py
│   ├── pipeline_runs.py
│   ├── add_run_id_to_counts.py
│   ├── cleanup_staging.py
│   │
│   └── source/
│       ├── orders_incremental.csv
│       ├── orders_incremental_2.csv
│       ├── orders_incremental_3.csv
│       └── orders_incremental_4.csv
│
├── database/
│   └── ecommerce.db
│
└── README.md
```

---

# How to Run the Incremental Pipeline

From the `Pipeline` directory:

```powershell
python pipeline.py orders_incremental_4.csv
```

The pipeline automatically executes:

```text
Extract
→ Stage
→ Validate
→ Save Rejected
→ Upsert
→ Update Watermark
→ Cleanup
```

The execution result is stored in the database.

---

# Production Considerations

This is a **production-style portfolio project**, not a claim of enterprise production infrastructure.

A larger production environment could use:

| Current Project | Production Upgrade |
|---|---|
| CSV files | APIs / database streams / CDC |
| Python execution | Airflow / Databricks / cloud orchestration |
| SQLite | PostgreSQL / cloud warehouse |
| Watermark ingestion | CDC or managed incremental ingestion |
| Local database | Cloud database/warehouse |
| Local execution | Cloud infrastructure |
| Manual monitoring | Automated alerts and observability |

For near-real-time source-system change capture, CDC could replace the current watermark-based approach.

---

# Key Learning Outcomes

This project demonstrates practical experience with:

- Data cleaning
- Data validation
- SQL
- Python
- Pandas
- SQLite
- Relational data modeling
- Incremental data processing
- Watermark-based ingestion
- Upsert logic
- Referential integrity
- Rejected-record handling
- Pipeline monitoring
- Failure handling
- Power BI
- DAX
- Business KPI analysis
- Production-oriented thinking

---

# Interview Summary

> I built an end-to-end e-commerce analytics platform using Python, SQL, SQLite, and Power BI. I started with intentionally imperfect raw datasets and performed data-quality validation and cleaning across customers, orders, products, order items, payments, and returns.
>
> I then created SQL-based business metrics such as revenue, orders, AOV, and profit and built a Power BI dashboard for business analysis.
>
> To make the project production-oriented, I implemented an incremental Python pipeline using a `modified_at` watermark. The pipeline extracts only new or changed records, stages them, validates them, separates rejected records, performs insert/update upserts, updates the watermark, records execution statistics, and cleans the staging layer.
>
> I also tested duplicate processing and failure scenarios to verify that the pipeline behaves correctly across repeated and unsuccessful runs.

---

# Project Status

```text
Business Requirements       ✅
Data Design                 ✅
Data Cleaning               ✅
SQL Fundamentals            ✅
Power BI Dashboard          ✅
Incremental Pipeline        ✅
Watermark Processing        ✅
Validation & Rejections     ✅
Upsert Processing           ✅
Pipeline Monitoring         ✅
Failure Testing             ✅
Staging Cleanup             ✅
Documentation               ✅
```

**Overall project: Completed as a production-style portfolio implementation.**
