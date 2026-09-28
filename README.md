# Brazilian Financial & Corporate Analytics Platform

An end-to-end analytics engineering project integrating Brazilian corporate fundamentals, macroeconomic indicators, and capital market data from official public sources.

## Project Overview

The platform will integrate data from three primary sources:

- **CVM** — corporate registry and financial statements;
- **Banco Central do Brasil (BCB)** — macroeconomic indicators through REST APIs;
- **B3** — listed companies, securities, sector classifications, and historical market data.

The project focuses on building a reproducible analytical pipeline using PostgreSQL, SQL, dbt, and Python, transforming heterogeneous public data into analytics-ready datasets.

## Core Objectives

The project is designed primarily to develop and demonstrate:

- PostgreSQL and relational database design;
- advanced SQL;
- REST API integration;
- dbt transformations, tests, documentation, and lineage;
- dimensional modeling;
- multi-source data integration;
- entity resolution across CVM and B3;
- financial and market time-series analysis;
- analytics marts.

## Planned Architecture

```text
CVM                    BCB                    B3
 │                      │                      │
CSV / ZIP            REST API          ZIP / fixed-width
 │                      │                      │
 └──────────────────────┼──────────────────────┘
                        ↓
                Python ingestion
                        ↓
                  PostgreSQL
                        ↓
                       dbt
          staging → intermediate → marts
                        ↓
               Analytics-ready data
                        ↓
                    Power BI
```

## Status

🚧 Project under active development.