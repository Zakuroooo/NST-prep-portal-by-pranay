# Faculty Portal

This is the Faculty Portal for PlacePrep, designed to track industry trends, curriculum gaps, and student session requests.

## Pages
- `/` - **Dashboard Home**: KPI overview, gap matrix preview, and live insights feed.
- `/requests` - **Session Requests**: View, confirm, or propose new times for student mock interviews.
- `/doubts` - **Doubts & Questions**: Answer student doubts organized by topic tags.
- `/curriculum` - **Curriculum Gap Matrix**: Heatmap visualization of syllabus coverage against industry demand.
- `/trends` - **Industry Trends**: Charting topic frequency and a feed of recent hiring trends.
- `/rankings` - **Company Rankings**: Sortable table of companies ranked by curriculum alignment.
- `/reports` - **Export Reports**: Generate and download PDF exports of the dashboard analytics.

## Data Layer (Mock)
All data is stored in `lib/data/`:
- `types.ts` - Shared TypeScript interfaces used across all data files.
- `curriculumCoverage.ts` - Data for the gap matrix heatmap and summary cards.
- `trendAlerts.ts` - Data for the insights feed on the dashboard and trends pages.
- `sessionRequests.ts` - Student session requests (pending, confirmed, etc.).
- `doubts.ts` - Threaded student questions and faculty replies.
- `companies.ts` - Company ranking data adapted from the main student portal.
- `reports.ts` - History of previously generated reports.

## Running Locally
The portal runs on port `3001` (if run concurrently with the student portal which uses `3000`).
```bash
npm run dev
```

## Implementation Notes
- The **Dashboard Home** (`/`) and **Curriculum Gap Matrix** (`/curriculum`) were built against specific visual mockups provided by Stitch:
  - `dashboard/student-portal/stitch_placeprep_nst_interview_intelligence_portal/faculty_dashboard_placeprep/`
  - `dashboard/student-portal/stitch_placeprep_nst_interview_intelligence_portal/curriculum_gap_matrix_placeprep/`
- The **Session Requests** (`/requests`) and **Doubts & Questions** (`/doubts`) mirror the exact data models and UI styling patterns of the Student Portal equivalents (`dashboard/student-portal/app/(app)/sessions/page.tsx` and `doubts/page.tsx`).
