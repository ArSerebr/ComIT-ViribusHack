# Projects — Student Opportunity Recommendation

Swipe-based recommendation feed for projects and opportunities. Multi-stage pipeline: candidate retrieval → feature hydration → multi-objective ranking → real-time profile adaptation.

## Quick start

```bash
py -m pip install -e .
set GIGACHAT_AUTH_KEY=your_base64_basic_key
py scripts/generate_data.py
py scripts/train_models.py
py scripts/run_feed.py --user-id user_0000 --max-cards 10
```

Falls back to local hash-based embeddings without `GIGACHAT_AUTH_KEY`.

## Structure

```
src/student_recsys/
  schema.py          unified card schema
  data_generation.py synthetic dataset generator
  features.py        embeddings and overlap features
  training.py        retrieval + ranker training
  pipeline.py        end-to-end recommendation service
scripts/             generate data, train models, run feed
notebooks/           ranker diagnostics (calibration, feature importance)
```

Algorithm details: `algo.md`.
