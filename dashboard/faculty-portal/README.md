# Faculty Portal

Next.js app for NST faculty — student monitoring, doubt replies, session management, rankings, and curriculum preview.

> **Architecture, data state, and known issues:** see [CONTEXT.MD](../../CONTEXT.MD) at the repo root.

## Pages

- `/` — Dashboard (KPIs, curriculum preview, industry trends from API)
- `/requests` — Session requests (accept / propose / decline)
- `/doubts` — Student doubts & replies
- `/students` — Student matrix
- `/rankings` — Company rankings
- `/leaderboard`, `/reports`, `/profile`, `/notifications`

**Disabled:** `/curriculum` and `/trends` routes return 404 (`notFound()`); UI exists only as commented code. Curriculum-gap API uses a heuristic formula — not full syllabus mapping.

## Data Layer

**Not mock.** Pages fetch from Next.js API routes → `placeprep-backend` → MongoDB. Some displayed metrics are still hardcoded (mock interview scores, avg response time) — see [CONTEXT.MD](../../CONTEXT.MD).

## Run Locally

```bash
cd dashboard/faculty-portal && npm run dev
```

Default port `3001` when run alongside the student portal on `3000`.

## Design References

Stitch HTML mockups (not wired into the app):

- `dashboard/student-portal/stitch_placeprep_nst_interview_intelligence_portal/faculty_dashboard_placeprep/`
- `dashboard/student-portal/stitch_placeprep_nst_interview_intelligence_portal/curriculum_gap_matrix_placeprep/`
