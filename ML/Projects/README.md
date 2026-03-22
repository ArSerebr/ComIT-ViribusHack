# Student Opportunity Recommendation System

This project implements the recommendation architecture described in `algo.md` for a swipe-based student opportunity feed.

Implemented stages:

- request context building
- weighted user interests and weighted user skills
- multi-source candidate retrieval from five content pools
- hydration with user-card and cross features
- hard and soft filtering
- multi-objective ranking for `open`, `like`, `share`, `long_view`, `skip_fast`, `disengage`
- final feed assembly with diversity controls
- online feedback update hook with real-time profile weight adaptation

## Project structure

- `config/settings.yaml` - data sizes, retrieval settings, ranking weights
- `src/student_recsys/schema.py` - unified card schema and shared constants
- `src/student_recsys/data_generation.py` - synthetic dataset generator
- `src/student_recsys/features.py` - embeddings and overlap features
- `src/student_recsys/training.py` - retrieval + ranker training
- `src/student_recsys/evaluation.py` - model quality analysis helpers
- `src/student_recsys/pipeline.py` - end-to-end recommendation service
- `scripts/generate_data.py` - create datasets
- `scripts/train_models.py` - train model artifacts
- `scripts/run_feed.py` - interactive one-card-at-a-time feed
- `notebooks/model_quality_review.ipynb` - notebook for ranker diagnostics

## Quick start

```bash
py -m pip install -e .
set GIGACHAT_AUTH_KEY=your_base64_basic_key
py scripts/generate_data.py
py scripts/train_models.py
py scripts/run_feed.py --user-id user_0000 --max-cards 10
```

The project now uses `GigaChat API` for card and user embeddings. If `GIGACHAT_AUTH_KEY` is not set, the code falls back to the local hash-based embedding generator so the scripts can still run offline.

## Notebook

Notebook for model quality analysis:

- `notebooks/model_quality_review.ipynb`

It includes:

- target-level ranker metrics
- calibration analysis
- feature importance review
- retrieval similarity diagnostics

Generated artifacts:

- `data/raw/users.csv`
- `data/raw/cards.csv`
- `data/raw/interactions.csv`
- `data/processed/ranker_training.csv`
- `models/retrieval.joblib`
- `models/ranker.joblib`
- `models/metadata.joblib`
