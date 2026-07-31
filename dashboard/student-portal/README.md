# Student Portal

Next.js app for NST students — company intel, practice, roadmaps, doubts, sessions, leaderboard, and onboarding.

> **Architecture, data state, and known issues:** see [CONTEXT.MD](../../CONTEXT.MD) at the repo root.

## Run Locally

```bash
# From repo root (after npm install)
cd dashboard/student-portal && npm run dev
```

Requires `MONGODB_URI` and `JWT_SECRET` (see `backend/.env.example`).

## Key Routes

- `/` — landing
- `/login`, `/register`, `/onboarding/*` — auth & onboarding
- `/dashboard`, `/companies`, `/roadmap`, `/practice` — core prep flows
- `/doubts`, `/sessions`, `/leaderboard`, `/submit` — mentoring & community

API routes live under `app/api/` and import `placeprep-backend` directly.
