# Schema

> **Not yet built.** This folder contains documentation only — no migration files, seed SQL, or ERD on disk.
>
> **Actual database:** MongoDB Atlas with Mongoose models in `backend/src/models/`. See [CONTEXT.MD](../CONTEXT.MD).

The SQL below is a **planned** normalized relational design from early project planning (originally intended for Supabase/PostgreSQL). It is **not** the running schema.

## Planned Structure (not implemented)

```
schema/
├── migrations/     # planned — does not exist
├── seed/           # planned — does not exist
└── erd.md          # planned — does not exist
```

## Planned Core Tables (reference only)

```sql
-- Companies
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  country TEXT DEFAULT 'India',
  tier TEXT  -- FAANG, Product, Service, Startup
);

-- Roles
CREATE TABLE roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,  -- SDE-1, SDE-2, Data Analyst, etc.
  level TEXT           -- Junior, Mid, Senior
);

-- Topics / Skill Areas
CREATE TABLE topics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,   -- Dynamic Programming, OS, DBMS, ML
  category TEXT                -- DSA, Core CS, Domain
);

-- Questions (core table)
CREATE TABLE questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id),
  role_id UUID REFERENCES roles(id),
  round_type TEXT,             -- coding, system_design, hr, managerial
  problem_summary TEXT,
  difficulty TEXT,             -- Easy, Medium, Hard
  source TEXT,                 -- geeksforgeeks, leetcode, etc.
  source_url TEXT,
  scraped_at TIMESTAMPTZ,
  frequency_score FLOAT DEFAULT 0.0
);

-- Many-to-many: questions <-> topics
CREATE TABLE question_topics (
  question_id UUID REFERENCES questions(id),
  topic_id UUID REFERENCES topics(id),
  PRIMARY KEY (question_id, topic_id)
);

-- B.Tech CS & AI Courses (for Use Case 2)
CREATE TABLE courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,          -- Data Structures & Algorithms, OS, DBMS
  semester INT
);

-- Syllabus topics linked to courses and the topic taxonomy
CREATE TABLE syllabus_topics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id UUID REFERENCES courses(id),
  topic_id UUID REFERENCES topics(id),
  coverage_depth TEXT          -- Introductory, Intermediate, Advanced
);
```

## Topic Taxonomy (reference)

| Category | Topics |
|----------|--------|
| DSA | Arrays, Strings, LinkedList, Trees, Graphs, DP, Greedy, Backtracking, Sorting, Hashing |
| Core CS | OS, DBMS, Networks, OOP, System Design, Compiler Design |
| Domain | Machine Learning, SQL, Web Dev, Cloud, DevOps |
| Behavioral | Communication, Leadership, Problem Solving |
