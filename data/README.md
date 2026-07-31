# Data

> **Folder not populated in repo.** This README describes the planned local data layout. Live data is in **MongoDB Atlas** (~678 companies, ~20,372 questions). See [CONTEXT.MD](../CONTEXT.MD).

Optional local exports: `pipeline/export_json.py` writes snapshots to `backend/src/data/` (gitignored when large).

## Planned Structure (not populated)

```
data/
├── raw/                   # Unmodified scraper output (JSON)
├── staging/               # Lightly cleaned, merged dumps pre-DB load
├── processed/             # Cleaned, normalized records
├── classified/            # Records tagged with topic, difficulty, round type
└── exports/               # Final exports for offline use
```

## Actual Data Lifecycle (today)

```
pipeline/01_ingestion/scrapers/github_repos.py
  → pipeline/ (ingest → dedupe → transform → classify → promote)
  → MongoDB Atlas (companies, questions collections)
  → Next.js API routes → portals
```

## Processed Record Shape (MongoDB / backend models)

See `backend/src/models/Question.ts` and `backend/src/models/Company.ts` for the canonical schema.

## Important Notes

- **Do not commit large data files.** Raw dumps belong in cloud storage or local-only paths.
- Preserve original raw inputs when adding new sources — never modify source files in place after ingestion.
