# Scrapers

> **Not yet built.** This folder contains documentation only — no scraper scripts exist here.
>
> **What works today:** GitHub LeetCode company-wise CSV ingestion lives in `pipeline/01_ingestion/scrapers/github_repos.py`. See [pipeline/README.md](../pipeline/README.md) and [CONTEXT.MD](../CONTEXT.MD).

The structure below describes the **planned** layout for 35+ source-specific scrapers. Only the GitHub repos parser has been implemented (under `pipeline/`, not here).

## Planned Structure (not implemented)

```
scrapers/
├── gfg.py               # GeeksForGeeks scraper
├── leetcode.py          # LeetCode Discuss (GraphQL API)
├── interviewbit.py      # InterviewBit scraper
├── ambitionbox.py       # AmbitionBox (Selenium/Playwright)
├── glassdoor.py         # Glassdoor scraper
├── hackerrank.py        # HackerRank scraper
├── coding_ninjas.py     # Coding Ninjas scraper
├── prepinsta.py         # PrepInsta scraper
├── naukri.py            # Naukri.com job listings
├── linkedin.py          # LinkedIn Jobs (API / scraper)
├── reddit.py            # Reddit (r/cscareerquestions, r/developersIndia)
├── github_repos.py      # → implemented in pipeline/ instead
└── utils/
    ├── browser.py
    ├── rate_limiter.py
    └── tos_check.py
```

## Planned Output Format

Each scraper would output JSON to `data/raw/<source_name>/`:

```json
{
  "source": "geeksforgeeks",
  "scraped_at": "2025-06-09T10:00:00Z",
  "records": [
    {
      "company": "Google",
      "role": "SDE-1",
      "round_type": "coding",
      "topic": "Dynamic Programming",
      "problem_summary": "...",
      "difficulty": "Medium",
      "source_url": "https://...",
      "raw_text": "..."
    }
  ]
}
```

## Planned Scraper Status

| Scraper | Status | Notes |
|---------|--------|-------|
| GitHub LeetCode CSV repos | ✅ Built | In `pipeline/01_ingestion/scrapers/github_repos.py` |
| GeeksForGeeks | 🔲 Not started | |
| LeetCode Discuss | 🔲 Not started | |
| InterviewBit | 🔲 Not started | |
| AmbitionBox | 🔲 Not started | |
| Glassdoor | 🔲 Not started | |
| All others in root README source list | 🔲 Not started | Aspirational — see root README |

## Before Building New Scrapers

1. Check ToS and robots.txt for the source
2. Use rate limiting — do not hammer any server
3. Never scrape behind a login wall without explicit permission
4. Wire output into `pipeline/` ingestion (see `pipeline/README.md`)
