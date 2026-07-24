# Scrapers

Source-specific scrapers and parsers for extracting raw interview data from 35+ public platforms.

## Structure

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
├── github_repos.py      # GitHub curated repos (REST API)
└── utils/
    ├── browser.py       # Shared Selenium/Playwright setup
    ├── rate_limiter.py  # Polite crawling delays
    └── tos_check.py     # robots.txt compliance checker
```

## Tech Stack

| Tool | Purpose |
|------|---------|
| `requests` + `BeautifulSoup` | Static HTML pages |
| `Selenium` / `Playwright` | JS-rendered pages |
| GraphQL / REST APIs | LeetCode, GitHub |
| `fake_useragent` | Rotate user agents |

## Output Format

Each scraper outputs a JSON file to `../data/raw/<source_name>/`:

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

## Before Running Any Scraper

1. Check `tos_check.py` output for the source
2. Confirm the source is in the approved list in `../docs/source_audit.md`
3. Use rate limiting — do not hammer any server
4. Never scrape behind a login wall without explicit permission

## Running a Scraper

```bash
pip install -r requirements.txt
python scrapers/gfg.py --company google --pages 10
```

## Status

| Scraper | Status | Notes |
|---------|--------|-------|
| GeeksForGeeks | 🔲 Not started | |
| LeetCode Discuss | 🔲 Not started | GraphQL endpoint available |
| InterviewBit | 🔲 Not started | |
| AmbitionBox | 🔲 Not started | JS-rendered, needs Playwright |
| Glassdoor | 🔲 Not started | May require login |
| Coding Ninjas | 🔲 Not started | |
| PrepInsta | 🔲 Not started | |
| Reddit | 🔲 Not started | Use Reddit API (PRAW) |
| GitHub Repos | 🔲 Not started | REST API available |
