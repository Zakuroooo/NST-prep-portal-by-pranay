# Pipeline

Ingestion, transformation, and export scripts that move data from raw JSON dumps into a clean, queryable Supabase database.

## Structure

```
pipeline/
├── ingest.py              # Load raw JSON from data/raw/ into staging DB table
├── deduplicate.py         # Remove duplicate questions across sources
├── transform.py           # Clean and normalize staging records
├── classify.py            # Claude API classification — topic, difficulty, round type
├── export.py              # Export classified data to data/exports/
├── run_all.py             # End-to-end pipeline runner
└── config.py              # DB connection, paths, constants
```

## Pipeline Flow

```
data/raw/
    ↓  ingest.py
  staging DB table
    ↓  deduplicate.py
  deduplicated records
    ↓  transform.py
  cleaned & normalized
    ↓  classify.py (Claude API)
  tagged records → Supabase DB
    ↓  export.py
  data/exports/ → Dashboard
```

## Running the Pipeline

```bash
# Step 1 — ingest raw data into staging
python pipeline/ingest.py --source geeksforgeeks

# Step 2 — deduplicate across all sources
python pipeline/deduplicate.py

# Step 3 — clean and normalize
python pipeline/transform.py

# Step 4 — classify with Claude API
python pipeline/classify.py

# Or run everything at once
python pipeline/run_all.py
```

## Environment Setup

Create a `.env` file in the project root:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
ANTHROPIC_API_KEY=your-claude-api-key
DB_STAGING_TABLE=raw_questions
DB_CLEAN_TABLE=questions
```

## Deduplication Strategy

Two records are considered duplicates if they share:
- Same `company` + `round_type` + `problem_summary` (fuzzy match >= 90%)
- Or same `source_url`

When duplicates are found, the record with the higher `frequency_score` is kept and sources are merged.

## Classification (Claude API)

`classify.py` sends each record to Claude and extracts:
- **Topic** — e.g., Dynamic Programming, System Design, SQL
- **Difficulty** — Easy / Medium / Hard (where not already present)
- **Round type** — coding, system_design, hr, managerial
- **Syllabus mapping** — which B.Tech course this maps to

## Status

| Script | Status |
|--------|--------|
| `ingest.py` | 🔲 Not started |
| `deduplicate.py` | 🔲 Not started |
| `transform.py` | 🔲 Not started |
| `classify.py` | 🔲 Not started |
| `export.py` | 🔲 Not started |
| `run_all.py` | 🔲 Not started |
