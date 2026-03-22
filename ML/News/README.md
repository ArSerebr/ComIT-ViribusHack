# News — Personalized News Feed

Weighted online recommendation model for student news. Balances personal relevance with freshness, source authority, and topic urgency. Profile weights update after every reaction.

## Quick start

```bash
set GIGACHAT_AUTH_KEY=your_basic_authorization_key
py generate_news_datasets.py           # regenerate datasets
py recommender.py --user-id user_0000 --limit 5
py realtime_news_test.py               # interactive swipe session
```

## Key files

| File | Purpose |
|------|---------|
| `generate_news_datasets.py` | Synthetic data: 320 users, 240 news, 15k interactions |
| `recommender.py` | Get top-N news for a user |
| `train_reaction_model.py` | Train online reaction update model |
| `realtime_news_test.py` | Interactive test with live profile updates |
| `gigachat_embedding_provider.py` | GigaChat API client with disk cache |
| `algo_v2.md` | Full algorithm description |

## Ranking logic

1. Filter stale or low-integrity cards
2. Retrieve from multiple strategies
3. Prefer fresher cards when relevance is comparable
4. Prefer more relevant cards when freshness is comparable
5. Recompute after every reaction
