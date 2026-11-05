# Automated Google Trends Data Pipeline
### *Databricks & dbt Core Orchestration Engine*

![Data Architecture](https://img.shields.io/badge/Architecture-ELT%20Multi--Hop-blue?style=for-the-badge)
![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=Databricks&logoColor=white)
![dbt Core](https://img.shields.io/badge/dbt_Core-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![Google BigQuery](https://img.shields.io/badge/Google_BigQuery-669DF6?style=for-the-badge&logo=Google%20Cloud&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## 1. Introduction

The **Automated Google Trends Data Pipeline** is an enterprise-grade ELT (Extract, Load, Transform) data engineering solution designed to extract, stage, and model high-velocity international search trend indices. 

By leveraging a decoupled Python extraction service, lightweight seed staging, and native **dbt Core (v2.0)** transformations executing directly inside **Databricks SQL Warehouse**, this architecture efficiently captures market dynamics across 13 European nations while ensuring strict schema validation, zero-loss historical persistence, and optimized warehouse compute utilization.

---

## 2. Objective of the Data Pipeline

Modern digital analytics demand continuous insight into shifting market interests without incurring high data warehousing compute overhead or overloading upstream APIs. The primary objectives of this pipeline are:

* **Efficient High-Velocity Extraction:** Systematically isolate top-performing rising search terms (strictly filtered at $\text{Rank} \le 20$) across multiple international regions over a rolling timeframe.
* **Decoupled Engine Execution:** Eliminate unnecessary network dependencies and cloud compute waste by executing data extraction via isolated scripts prior to warehouse ingestion.
* **Stateless Staging to Immutable Production:** Mitigate downstream pollution by utilizing volatile, self-cleaning staging layers paired with incremental, append-only historical ledgers.
* **Modern Warehouse Native Modeling:** Offload heavy analytical processing directly to the cloud compute engine using `dbt Core` connected to Databricks.

---

## 3. Component Breakdown & Architectural Flow

The pipeline executes a decoupled multi-hop architecture designed to maximize data reliability while preserving warehouse performance:

```
┌────────────────────────┐
│  Google BigQuery       │  (Public Google Trends Dataset)
└───────────┬────────────┘
            │  1. REST API Extraction via Python
            ▼
┌────────────────────────┐
│  Local Disk (.csv)     │  (Lightweight Seed Packet: raw_trends.csv)
└───────────┬────────────┘
            │  2. dbt seed Injection Layer
            ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        DATABRICKS WAREHOUSE                            │
│                                                                        │
│   ┌────────────────────┐      ┌─────────────────────────┐              │
│   │   default_raw      ├─────►│    stg_daily_trends     │              │
│   │ (Volatile Seed)    │      │   (Standardized View)   │              │
│   └────────────────────┘      └────────────┬────────────┘              │
│                                            │                           │
│                                            │ 3. Native dbt Transform   │
│                                            ▼                           │
│                               ┌─────────────────────────┐              │
│                               │    historical_trends    │              │
│                               │ (Incremental Ledger)    │              │
│                               └─────────────────────────┘              │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Pipeline Execution Stages

1. **Extraction (Google BigQuery REST API):** A decoupled Python extraction pipeline queries the public Google Trends dataset via standard REST endpoints. It isolates the top rising terms across 13 targeted European nations ($\text{Rank} \le 20$) over a rolling time window, minimizing API footprint and bandwidth consumption.
2. **Ingestion & Seed Injection:** The extracted data packet is saved locally as `raw_trends.csv`. The orchestrator executes `dbt seed`, which dynamically drops pre-existing target structures and recreates a clean, raw dataset directly in Databricks (`default_raw`).
3. **Transformation & Analytical Modeling:** `dbt Core` manages multi-tier SQL transformations natively within Databricks, executing data casting, sanitization, alias mapping, and incremental appends to the production warehouse tables.

---

## 4. Data Model Breakdown & Execution Logic

The data layer follows a classic three-tier architecture configured via `dbt_project.yml` to balance storage efficiency and query performance:

| Layer | Resource Type | Materialization | Strategy & Execution Behavior |
| :--- | :--- | :--- | :--- |
| **`raw_trends`** | `dbt Seed` | Table | **Volatile / Destructive Reload:** Completely recreated on each run via `dbt seed`. Guarantees zero stale state leakage from prior runs. |
| **`stg_daily_trends`** | `dbt Model` | View | **Non-Persistent Abstraction:** Cleans raw inputs, casts data types, strips whitespace, and standardizes column aliases (`search_keyword`, `search_rank`, `traffic_percent_gain`) without extra storage costs. |
| **`historical_trends`** | `dbt Model` | Table | **Incremental Ledger:** Merges and appends fresh daily trend snapshots into a permanent analytical baseline, creating a continuous historical time-series. |

---

## 5. Core Configuration (`dbt_project.yml`)

The project configuration defines static analysis behavior and materialization paths directly aligned with modern engine standards:

```yaml
name: 'trends_dbt'
version: '1.0.0'
config-version: 2
profile: 'trends-dbt'

seed-paths: ["seeds"]
model-paths: ["models"]
macro-paths: ["macros"]

clean-targets:
  - "target"
  - "dbt_packages"

seeds:
  trends_dbt:
    +enabled: true

models:
  trends_dbt:
    +static_analysis: "off"
    # Materialization rules for processing layers
    stg_daily_trends:
      +materialized: view
    historical_trends:
      +materialized: table
```

---

## 6. Local Execution & Operations

### Prerequisites
* **Python 3.10+** (managed via [`uv`](https://github.com/astral-sh/uv))
* **dbt Core v2.0+** with `dbt-databricks` adapter installed
* Configured Databricks SQL Warehouse connection profile (`~/.dbt/profiles.yml`)

### Execution Workflow
Execute the end-to-end lifecycle—clearing target build logs, extracting fresh BigQuery data, injecting seeds, and compiling dbt models:

```bash
# 1. Purge legacy compilation files and structural artifacts
uv run dbt clean

# 2. Trigger the automated extraction and execution workflow
uv run python python_run_pipeline.py
```

---

## 7. Roadmap & Future Enhancements

- [ ] **Cloud Orchestration:** Automate scheduled pipeline runs via **Google Cloud Run** container jobs or **Windows Automatic Pipe Runner**.
- [ ] **CI/CD Integration:** Implement GitHub Actions for automated code linting, `dbt test` execution, and schema regression checks.
- [ ] **Alerting & Data Quality Monitoring:** Integrate target freshness checks and failure alerting via Slack/Email Webhooks.
