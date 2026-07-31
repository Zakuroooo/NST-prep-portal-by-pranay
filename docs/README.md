# Docs

Project documentation, research notes, and analysis outputs.

> **Current architecture and project state:** see [CONTEXT.MD](../CONTEXT.MD) at the repo root.

## What Exists Today

```
docs/
├── README.md                    # this file
└── scraping_pipeline_v1.txt     # Internal pipeline planning doc (June 2026; some sections describe planned PostgreSQL/Airflow — superseded by MongoDB implementation in pipeline/)
```

## Planned Structure (not yet created)

```
docs/
├── source_audit.md
├── data_dictionary.md
├── architecture.md
├── weekly_updates/
├── gap_analysis/
└── decisions/
```

When adding new docs, prefer updating `CONTEXT.MD` for anything about stack, data reality, or known bugs — keep this folder for research, audits, and analysis write-ups.
