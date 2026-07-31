# PlacePrep Data Pipeline

This pipeline ingests, deduplicates, cleans, classifies, and promotes LeetCode questions from **GitHub LeetCode company-wise CSV repos** into MongoDB (`companies`, `questions`) for the portals. **Status: working** for that one source (~678 companies, ~20,372 questions loaded).

> **Architecture & data state:** see [CONTEXT.MD](../CONTEXT.MD) at the repo root.

## Environment Setup
Make sure you have a `.env` file in this directory with the following variables before running any scripts:
```
MONGO_URI="mongodb+srv://..."
MONGO_DB_NAME="placeprep_staging"
```

## Pipeline Execution Order

The scripts are organized sequentially by stage. All scripts should be run from their respective directories or from the root `pipeline/` directory (e.g., `python 01_ingestion/ingest.py`).

### Stage 1: Setup
Run these once to configure the database schema and initial data.
1. `python setup/setup_mongo_schema.py` - Sets up MongoDB collections, validation rules, and indexes.
2. `python setup/bootstrap_companies.py` - Seeds the `companies` collection from unique company slugs found in the raw scraped CSVs.

### Stage 2: Ingestion
1. `python 01_ingestion/ingest.py` - Reads raw scraped CSV files, validates them using Pydantic, and bulk-inserts them into the `raw_scraped_data` collection.

### Stage 3: Processing
1. `python 02_processing/deduplicate.py` - Finds exact duplicate questions across different sources and marks them with `status: "duplicate"`.
2. `python 02_processing/transform.py` - Links raw records to their proper `companyId` in the `companies` collection and marks them as `status: "clean"`.

### Stage 4: Classification
1. `python 03_classification/classify_from_kaggle.py` - Matches clean records against the official Kaggle LeetCode dataset to attach real topic tags (e.g., "Arrays", "Hash Tables") for free, marking them `status: "classified"`.

### Stage 5: Promotion & Aggregation
1. `python 04_promotion/promote.py` - Copies every "classified" record into the final `questions` collection matching the exact backend schema.
2. `python 04_promotion/aggregate.py` - Recalculates `topicFrequency` and `difficultyDistribution` on every company document based on its promoted questions.

---

*Note: The `tests/` and helper classification scripts (`export_for_classification.py`, `merge_classification_results.py`, `classify.py`) are kept for fallback manual/AI labeling of unmatched records.*
