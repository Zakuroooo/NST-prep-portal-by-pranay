# Data

Storage for all raw and processed datasets at every stage of the pipeline.

## Structure

```
data/
├── raw/                   # Unmodified scraper output (JSON)
│   ├── geeksforgeeks/
│   ├── leetcode/
│   ├── interviewbit/
│   ├── ambitionbox/
│   ├── glassdoor/
│   └── ...
├── staging/               # Lightly cleaned, merged dumps pre-DB load
├── processed/             # Cleaned, normalized, schema-conformant records
├── classified/            # Records tagged with topic, difficulty, round type
└── exports/               # Final exports for dashboard consumption
```

## Data Lifecycle

```
scrapers/ → data/raw/ → data/staging/ → data/processed/ → data/classified/ → Supabase DB
```

| Folder | Stage | Who writes here |
|--------|-------|----------------|
| `raw/` | Post-scrape | Scrapers |
| `staging/` | Post-merge | Ingestion pipeline |
| `processed/` | Post-cleaning | Transformation scripts |
| `classified/` | Post-AI tagging | Claude API classification |
| `exports/` | Pre-dashboard | Export scripts |

## Schema (Processed Records)

Each record in `processed/` and `classified/` conforms to:

```json
{
  "id": "uuid",
  "company": "Google",
  "role": "SDE-1",
  "round_type": "coding | system_design | hr | managerial",
  "topic": "Dynamic Programming",
  "problem_summary": "Given an array...",
  "difficulty": "Easy | Medium | Hard",
  "source": "geeksforgeeks",
  "source_url": "https://...",
  "scraped_at": "2025-06-09T10:00:00Z",
  "frequency_score": 0.73
}
```

## Important Notes

- **Do not commit large data files.** Raw dumps can be large — store in cloud storage (Supabase Storage / Google Drive) and add to `.gitignore`.
- `data/raw/` is in `.gitignore` by default. Only commit small sample files for testing.
- Always preserve original raw files — never modify `raw/` in place.
