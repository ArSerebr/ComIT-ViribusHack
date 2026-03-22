# Student News Recommendation System

This project now implements the weighted online recommendation architecture from `algo_v2.md` for a swipe-based student news feed.

The core idea stayed the same:

- weighted user interests
- weighted user skills
- real-time profile adaptation after each reaction
- multi-objective ranking over `open`, `like`, `share`, `long_view`, `skip_fast`, `disengage`

The news-specific change is ranking priority:

- the feed should surface the freshest news that is personally relevant to the student
- recency, topic urgency, source authority, and actionability now play a central role

## GigaChat embeddings

The project is now integrated with GigaChat API for embeddings.

Used flow:

1. get OAuth token from `https://ngw.devices.sberbank.ru:9443/api/v2/oauth`
2. optionally check available models from `https://gigachat.devices.sberbank.ru/api/v1/models`
3. request embeddings from `https://gigachat.devices.sberbank.ru/api/v1/embeddings`

Code entry point:

- `gigachat_embedding_provider.py`

Set the authorization key before generation or inference:

```powershell
$env:GIGACHAT_AUTH_KEY="your_basic_authorization_key"
```

Optional settings:

- `GIGACHAT_SCOPE` default: `GIGACHAT_API_PERS`
- `GIGACHAT_EMBEDDING_MODEL` default: `Embeddings`
- `GIGACHAT_VERIFY_SSL` default: `true`
- `GIGACHAT_TIMEOUT_SECONDS` default: `60`

Embeddings are cached on disk in:

- `.cache/gigachat_embeddings.json`

## Files in this project

- `algo_v2.md` - full description of the news-only weighted online algorithm
- `generate_news_datasets.py` - synthetic dataset generator for student users, news cards, interactions, and ranker rows
- `data/raw/students.csv` - student profiles with weighted interests, weighted skills, freshness preference, and source loyalty
- `data/raw/news.csv` - news cards only
- `data/raw/interactions.csv` - simulated swipe-feed interactions
- `data/processed/news_ranker_training.csv` - ranker-ready features and labels

## Dataset design

The generated data is aligned with the new news recommendation logic:

- users are still students
- cards are now only news
- news includes freshness, urgency, source authority, breaking score, and actionability
- interactions are generated from a session simulation with online profile updates
- ranker features include both personalization signals and timeliness signals

## Regenerate datasets

Run:

```bash
py generate_news_datasets.py
```

If `GIGACHAT_AUTH_KEY` is set, card embeddings in the regenerated datasets will be built through GigaChat API.

The generator recreates:

- `data/raw/students.csv`
- `data/raw/news.csv`
- `data/raw/interactions.csv`
- `data/processed/news_ranker_training.csv`

## Run recommender

Get top personal news for a user:

```bash
py recommender.py --user-id user_0000 --limit 5
```

Or return JSON:

```bash
py recommender.py --user-id user_0000 --limit 5 --json
```

At runtime the user profile embedding is also built through the shared GigaChat embedding provider.

## Train reaction model

Train a separate lightweight model for online reaction updates:

```bash
py train_reaction_model.py
```

This creates:

- `models/reaction_update_model.json`

## Real-time interactive test

Run an interactive test session:

```bash
py realtime_news_test.py
```

Then:

1. enter `student_id`
2. get the best matching news right now
3. choose one of 3 reactions:

- `1` - just viewed
- `2` - liked
- `3` - read more

After every reaction:

- the next best news is recalculated
- interest and skill weights shift slightly
- the script shows why the news matched the student

Current generated sizes:

- `users`: 320
- `cards`: 240
- `interactions`: 15312
- `ranker_training`: 15312

## News schema highlights

Important card fields include:

- `topics`
- `skills_required`
- `skills_gained`
- `news_category`
- `published_at`
- `updated_at`
- `freshness_timestamp`
- `source_name`
- `source_authority`
- `topic_urgency`
- `actionability_relevance`
- `recency_score`
- `breaking_score`
- `embedding_vector`

## Ranking focus

The intended ranking behavior is:

1. filter low-integrity or stale cards
2. retrieve relevant news from multiple strategies
3. prefer fresher cards when relevance is comparable
4. prefer more personally relevant cards when freshness is comparable
5. update the profile after every reaction and recompute the next recommendation
