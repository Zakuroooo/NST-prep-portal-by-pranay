# Schema

Database schema definitions, migration files, and the Entity Relationship Diagram for the normalized interview data model.

## Structure

```
schema/
├── migrations/
│   ├── 001_create_companies.sql
│   ├── 002_create_roles.sql
│   ├── 003_create_topics.sql
│   ├── 004_create_questions.sql
│   ├── 005_create_question_topics.sql
│   ├── 006_create_courses.sql
│   └── 007_create_syllabus_topics.sql
├── seed/
│   ├── companies.sql        # Seed known company names
│   └── topics.sql           # Seed standard topic taxonomy
└── erd.md                   # Entity Relationship Diagram
```

## Core Tables

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

## Entity Relationship Diagram

```
companies ──< questions >── roles
                  │
            question_topics
                  │
               topics
                  │
          syllabus_topics
                  │
               courses
```

## Running Migrations

```bash
# Using Supabase CLI
supabase db push

# Or directly via psql
psql $DATABASE_URL -f schema/migrations/001_create_companies.sql
```

## Topic Taxonomy

Standard categories used across the project:

| Category | Topics |
|----------|--------|
| DSA | Arrays, Strings, LinkedList, Trees, Graphs, DP, Greedy, Backtracking, Sorting, Hashing |
| Core CS | OS, DBMS, Networks, OOP, System Design, Compiler Design |
| Domain | Machine Learning, SQL, Web Dev, Cloud, DevOps |
| Behavioral | Communication, Leadership, Problem Solving |
