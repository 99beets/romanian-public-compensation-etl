# ADR 0003 — Use dbt for SQL-based transformations instead of Python

## Status
Accepted

## Context
After raw data is cleaned and loaded into PostgreSQL, additional transformations are required to:
- normalize people and organization entities
- deduplicate identities
- model fact and dimension tables
- support analytical queries and quality checks

These transformations could be implemented in Python (pandas) before loading, or inside the database using SQL.

The project already uses PostgreSQL as the analytical store and aims to demonstrate production-style data modeling practices.

## Decision
All analytical transformations beyond basic cleaning and normalization are implemented in **dbt using SQL models**, not in Python.

Python is responsible only for:
- extraction
- structural validation
- data cleaning
- safe loading into Postgres

Relational modeling and analytics are handled entirely inside the database via dbt.

## Consequences
### Benefits
- **Separation of concerns**: Python handles ingestion; dbt handles modeling
- **Testability**: dbt provides schema and data tests close to the models
- **Lineage visibility**: dbt docs show dependencies between models
- **Warehouse-native execution**: transformations run where the data lives
- **Industry alignment**: mirrors real analytics engineering workflows

### Trade-offs / Costs
- Requires maintaining both Python and dbt project structures
- SQL transformations may be less expressive than Python for complex text parsing
- Adds an additional tool that contributors must learn

## Alternatives considered
1) **Do all transformations in Python before loading**
   - Simpler pipeline structure
   - Loses benefits of warehouse-native testing and lineage

2) **Hybrid approach (some SQL, some Python)**
   - Flexible
   - Increases cognitive overhead and harder to reason about data ownership

## Notes / Future evolution
If the dataset grows significantly or moves to columnar warehouses (e.g., BigQuery, Redshift),
the dbt models can be reused with minimal changes, while Python ingestion logic remains largely unchanged.
