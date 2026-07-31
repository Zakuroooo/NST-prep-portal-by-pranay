# PlacePrep — Project Context (Source of Truth)

> **Update this file** when architecture, data state, or known issues change. Other READMEs should link here instead of duplicating this content.

## Architecture

- **Monorepo:** npm workspaces — `backend/` + `dashboard/student-portal`, `dashboard/faculty-portal`, `dashboard/admin-portal`
- **Backend:** Shared TypeScript service layer (`placeprep-backend`) — Mongoose models, repositories, services, validators. **No standalone HTTP server.**
- **API pattern:** Each portal's Next.js API routes import the backend package directly: `Route → Service → Repository → MongoDB`
- **Database:** MongoDB Atlas (`MONGODB_URI`) — **not** Supabase/PostgreSQL
- **Auth:** JWT in HTTP-only cookies + role middleware (`requireStudent`, `requireFaculty`, `requireAdmin`) — **not** Supabase Auth
- **Deployment:** Three separate Next.js apps on Vercel (see root README for URLs)
- **Data pipeline:** Python ETL in `pipeline/` → MongoDB collections (`companies`, `questions`, etc.)

## Repository Layout

```
├── backend/           # Shared TS service layer (imported by portal API routes)
├── dashboard/
│   ├── student-portal/
│   ├── faculty-portal/
│   └── admin-portal/
├── pipeline/          # Working Python MongoDB ETL (GitHub LeetCode CSV repos)
├── scrapers/          # README only — planned, not built
├── schema/            # README only — planned PostgreSQL design, not used
├── data/              # README only — planned local data folders, not populated in repo
└── docs/              # Misc docs (see docs/README.md)
```

## Data: Real vs Mock / Heuristic

| What | Status |
|------|--------|
| **Companies & questions in MongoDB** | **Real** — ~678 companies, ~20,372 questions (GitHub LeetCode company-wise CSV repos via `pipeline/`) |
| **Student practice / company pages** | Served from MongoDB question/company collections |
| **Practice category totals** (e.g. "2400 DSA" in UI constants) | **Hardcoded** — not computed from DB |
| **Faculty mock-interview scores, avg response time** | **Hardcoded / mocked** in backend service |
| **Faculty curriculum-gap analysis** | Uses real question topic counts but **heuristic formula** + hardcoded subject list — not syllabus-backed |
| **Seed script** (`backend/src/scripts/seed.ts`) | Demo users, doubts, sessions, etc.; does not replace pipeline company/question data |
| **JSON exports** (`backend/src/data/*.json`) | Local MongoDB snapshots via `pipeline/export_json.py`, not used at runtime |

## Scrapers & Sources

- **Built and ingested:** 1 source — GitHub LeetCode company-wise CSV repos (`pipeline/01_ingestion/scrapers/github_repos.py`)
- **Planned, not built:** The 35+ sources listed in the root README; `scrapers/` has no code yet
- **Aspirational source list:** Root README data-source tables = target inventory, not current coverage

## Feature Completeness (High Level)

| Area | Status |
|------|--------|
| Student portal (companies, practice, roadmaps, doubts, sessions, auth) | Largely built, wired to MongoDB |
| Faculty portal (dashboard, doubts, sessions, students, rankings) | Built; curriculum/trends **dedicated pages disabled** (`notFound()`) |
| Admin portal (overview, analytics, faculty mgmt) | Built |
| Curriculum intelligence (Use Case 2) | Partial — API preview on faculty home; full gap matrix / syllabus mapping **not done** |
| `scrapers/`, `schema/`, `data/` folders | Documentation placeholders only |

## Known Bugs & Data Issues

- **Roadmap progress display:** Roadmap cards count `week.questions.length`, but API weeks store progress in `doneQuestions` / `totalQuestions` with empty `questions` arrays → progress can show **0%**
- **Topic name mismatches:** Roadmap week labels (e.g. `"Arrays & Strings"`) may not match DB topic tags (e.g. `"Arrays"`, `"Strings"`) → empty question lists for some weeks
- **LeetCode links:** Many question records have `leetcodeUrl: null`; link may exist on `sourceUrl` instead
- **`isSeeded` flag:** Pipeline-promoted records also carry `isSeeded: true`, which can confuse seed/wipe logic

## Local Dev (Quick Reference)

```bash
# From repo root — install workspaces
npm install

# Each portal (separate terminal; default ports vary)
cd dashboard/student-portal && npm run dev   # :3000
cd dashboard/faculty-portal && npm run dev   # :3001
cd dashboard/admin-portal && npm run dev     # :3002

# Backend env: copy backend/.env.example → backend/.env (or portal .env.local with MONGODB_URI, JWT_SECRET)
# Pipeline env: pipeline/.env with MONGO_URI, MONGO_DB_NAME
```

See `pipeline/README.md` for ETL run order. See `backend/package.json` for `npm run seed`.
