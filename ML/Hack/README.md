# Hack — Hackathon Recommendation Pipeline

Recommendation model for matching students with hackathons. Same architecture as `Projects/` but tuned for event-based content with deadline and skill-fit signals.

## Quick start

```bash
py -m pip install -e .
set GIGACHAT_AUTH_KEY=your_base64_basic_key
py scripts/generate_data.py
py scripts/train_models.py
py scripts/run_feed.py --user-id user_0000 --max-cards 10
```

Falls back to local hash-based embeddings if `GIGACHAT_AUTH_KEY` is not set.

## Structure

```
config/settings.yaml       retrieval and ranking weights
src/student_recsys/        schema, features, training, pipeline
scripts/                   generate data, train, run feed
notebooks/                 ranker diagnostics
```
