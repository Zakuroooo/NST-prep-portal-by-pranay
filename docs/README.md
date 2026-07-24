# Docs

Project documentation, research notes, audit reports, and analysis outputs.

## Structure

```
docs/
├── source_audit.md          # Week 1 — scrapability, ToS, robots.txt findings per source
├── data_dictionary.md       # Field definitions and allowed values
├── architecture.md          # Full system architecture with diagrams
├── weekly_updates/
│   ├── week1.md
│   ├── week2.md
│   └── ...
├── gap_analysis/
│   ├── methodology.md       # How gap analysis is computed
│   └── findings.md          # Results — industry vs syllabus comparison
└── decisions/
    ├── schema_v1.md         # Why we chose this schema
    └── tech_stack.md        # Tech stack decisions and trade-offs
```

## Key Documents

### `source_audit.md`
Produced in Week 1. For each data source documents:
- Is it scrapable? (Yes / Partial / No)
- ToS and robots.txt status
- Data quality assessment
- Estimated record count
- Recommended scraping approach

### `data_dictionary.md`
Canonical definitions for every field in the schema:

| Field | Type | Allowed Values | Notes |
|-------|------|---------------|-------|
| `round_type` | enum | coding, system_design, hr, managerial | |
| `difficulty` | enum | Easy, Medium, Hard | null if not available |
| `tier` | enum | FAANG, Product, Service, Startup | company classification |
| `coverage_depth` | enum | Introductory, Intermediate, Advanced | syllabus only |

### `gap_analysis/findings.md`
Output of Use Case 2 analysis:
- Topics that appear in 30%+ of company interviews but have low syllabus coverage
- Topics with high syllabus coverage but low industry frequency
- Per-course alignment scores

## Weekly Updates

Each week, add a brief update to `weekly_updates/weekN.md` covering:
- What was completed
- Blockers encountered
- Data quality observations
- Decisions made

## Contributing to Docs

If you discover something important about a data source, an edge case in the schema, or a decision that was made — document it here. Future team members will thank you.
