# Weighted Real-Time Recommendation Algorithm for Student News Feed

## 1. Purpose

This document describes the news-only version of the weighted recommendation algorithm.

The logic stays the same as in the previous weighted online system:

- weighted interests
- weighted skills
- stronger influence of skills than interests
- real-time profile adaptation after every card reaction

The difference is product focus.

Instead of ranking mixed opportunity cards, the system now ranks personalized news for students and prioritizes the most relevant fresh stories.

---

## 2. Product behavior

The product shows one news card at a time in a swipe-like feed.

Every card has `card_type = news`.

For every shown card, the user can react with:

- `open`
- `like`
- `share`
- `long_view`
- `skip_fast`
- `disengage`

After each reaction:

1. the interaction is saved
2. user profile weights are updated
3. the next recommendation is recalculated

This keeps the feed adaptive inside the session.

---

## 3. Core idea

The system still treats onboarding preferences as weighted signals, not flat tags:

- each topic has its own weight
- each skill has its own weight
- skill weights influence ranking more strongly
- fresh reactions update both maps online

For news, this matters because two students with the same topics can still want very different stories:

- one may want breaking policy updates
- another may prefer deep research explainers
- another may care most about fast-moving product launches in their skill area

---

## 4. User profile model

Each user profile contains:

- `user_id`
- `interests`
- `skills`
- `interest_weights`
- `skill_weights`
- `experience_level`
- `preferred_language`
- `region`
- `preferred_formats`
- `freshness_preference`
- `breaking_affinity`
- `source_loyalty_weights`

### 4.1 Interest weights

`interest_weights` models topic relevance, for example:

```json
{
  "ai": 1.46,
  "policy": 1.12,
  "climate": 0.81
}
```

### 4.2 Skill weights

`skill_weights` models the lens through which a student reads news:

```json
{
  "python": 1.58,
  "analytics": 1.31,
  "react": 0.74
}
```

### 4.3 News-specific preferences

The news version adds explicit timeliness and source signals:

- `freshness_preference` controls how strongly recency should matter
- `breaking_affinity` controls appetite for urgent updates
- `source_loyalty_weights` captures trusted outlets

---

## 5. Request context

For each feed request, the system builds a request context containing:

### 5.1 User profile fields

- weighted interests
- weighted skills
- preferred language
- region
- preferred formats
- freshness preference
- breaking affinity
- trusted source weights

### 5.2 Behavioral fields

- recently opened cards
- recently liked cards
- recently shared cards
- skipped cards
- dwell time statistics
- source engagement
- category engagement

### 5.3 Session fields

- current session depth
- recent interaction streak
- novelty state
- diversity state
- freshness state

---

## 6. Candidate sourcing

The news system keeps the same multi-source retrieval logic, but all retrieval operates inside the news pool.

Candidates can come from:

1. weighted onboarding similarity retrieval
2. weighted behavioral retrieval
3. embedding retrieval
4. exploration retrieval
5. trending and breaking retrieval

### 6.1 Weighted onboarding retrieval

For each candidate news card:

- card topics are compared with `interest_weights`
- card reading-context skills are compared with `skill_weights`

Weighted onboarding score:

```text
OnboardingScore(card) =
  a1 * WeightedTopicMatch
+ a2 * WeightedSkillMatch
+ a3 * FreshnessPreferenceAlignment
```

Where:

- `a2 > a1`
- `a3` is high enough to favor new relevant stories over stale relevant stories

### 6.2 Weighted behavioral retrieval

The system builds temporary behavioral maps from recent positive interactions:

- topics from engaged cards increase behavioral topic affinity
- skills from engaged cards increase behavioral skill affinity
- trusted sources and frequently opened categories increase retrieval weight

### 6.3 Embedding retrieval

The user embedding is built from:

- weighted interests
- weighted skills
- recent positive news interactions

The card embedding is built from:

- topics
- contextual skills
- source metadata
- news category

Candidates are retrieved by user-card embedding similarity.

### 6.4 Breaking and trending retrieval

This source explicitly injects:

- very recent cards
- high-urgency cards
- high-authority source cards

This prevents the system from missing major updates that are both timely and personally relevant.

---

## 7. Unified news card schema

All candidates are transformed into one rankable news schema.

Core fields:

- `card_id`
- `card_type`
- `title`
- `short_description`
- `full_description`
- `topics`
- `skills_required`
- `skills_gained`
- `news_category`
- `format`
- `language`
- `location`
- `published_at`
- `updated_at`
- `freshness_timestamp`
- `source_name`
- `source_type`
- `author_name`
- `estimated_read_time_minutes`
- `quality_score`
- `popularity_score`
- `editorial_priority`
- `source_authority`
- `topic_urgency`
- `actionability_relevance`
- `recency_score`
- `breaking_score`
- `novelty_score`
- `integrity_score`
- `status`
- `embedding_vector`

---

## 8. Hydration layer

After retrieval, every news card is enriched with ranking features.

### 8.1 Weighted user-card features

The system computes:

- `topic_overlap_score`
- `skill_overlap_score`
- `skill_gain_score`
- `interest_weight_mean`
- `skill_weight_mean`
- `interest_match_count`
- `skill_match_count`

### 8.2 News-specific ranking features

The system also computes:

- `format_match`
- `language_match`
- `region_match`
- `freshness_alignment_score`
- `source_loyalty_score`
- `breaking_affinity_score`
- `retrieval_similarity`
- `recent_open_rate`
- `recent_like_rate`
- `recent_share_rate`
- `recent_skip_rate`
- `category_entropy`
- `session_depth_mean`

### 8.3 Timeliness logic

Timeliness is not pure recency.

It combines:

- freshness of the article
- user preference for fresh content
- topic urgency
- source authority
- actionability of the update

This helps recommend news that is not only new, but new in a way that matters for that student.

---

## 9. Filtering layer

Hard filters remove cards that should not be shown:

- inactive or hidden content
- low-integrity content
- recently shown duplicates
- stale content below freshness threshold
- hard language restrictions when required

Soft filters reduce rank probability:

- repeated source exposure
- repeated category exposure
- low novelty
- low timeliness fit

---

## 10. Ranking layer

The ranker remains multi-objective.

For each candidate it predicts:

- `P(open)`
- `P(like)`
- `P(share)`
- `P(long_view)`
- `P(skip_fast)`
- `P(disengage)`

### 10.1 Ranker inputs

The ranker uses:

- user embedding
- candidate embedding
- weighted topic overlap
- weighted skill overlap
- weighted skill gain score
- source authority
- topic urgency
- actionability relevance
- recency score
- breaking score
- freshness alignment
- source loyalty
- session and behavior aggregates

### 10.2 Final score

Final score is a weighted combination:

```text
FinalScore(card) =
  w1 * P(open)
+ w2 * P(like)
+ w3 * P(share)
+ w4 * P(long_view)
- w5 * P(skip_fast)
- w6 * P(disengage)
+ w7 * FreshnessBoost
+ w8 * UrgencyBoost
+ w9 * SourceAuthorityBoost
+ w10 * DiversityBoost
- SoftFilterPenalty
```

The news-specific rule is:

- among similarly relevant cards, the fresher one should rank higher
- among similarly fresh cards, the more personally relevant one should rank higher

---

## 11. Real-time profile adaptation

This remains the main online component.

After every reaction, the system updates the profile immediately.

### 11.1 Update principle

Each card contains:

- `topics`
- `skills_required`
- `skills_gained`

Depending on the reaction:

- related topics update `interest_weights`
- related skills update `skill_weights`

### 11.2 Reaction update strengths

Positive reactions increase weights:

- `open`
- `like`
- `share`
- `long_view`

Negative reactions decrease weights:

- `skip_fast`
- `disengage`

### 11.3 Different update strength for interests and skills

In the current design:

- skills are updated more aggressively than interests
- `skills_required` are updated stronger than `skills_gained`

This keeps the feed aligned not only with broad curiosity, but also with the student's reading lens.

### 11.4 Cold-start expansion

If a news card contains a topic or skill not yet present in the profile:

- it may be inserted
- it starts from a cold-start weight
- future reactions then strengthen or weaken it

This allows the profile to evolve beyond onboarding.

### 11.5 Weight boundaries

To prevent instability, profile weights are clipped between minimum and maximum limits.

---

## 12. Real-time loop

The online loop for one session is:

1. build request context
2. retrieve news candidates from all retrieval sources
3. hydrate candidates with weighted and freshness-aware features
4. filter ineligible candidates
5. score candidates
6. assemble final feed
7. display top card
8. wait for user reaction
9. save interaction
10. update interest and skill weights
11. recompute next recommendation

Recommendations are therefore session-adaptive and freshness-aware.

---

## 13. Display behavior

The interactive feed should show three clearly separated blocks.

### 13.1 Card Content

- title
- descriptions
- topics
- contextual skills
- source
- category
- publication and update timestamps

### 13.2 Model Signals

- retrieval strategy
- retrieval similarity
- freshness score
- urgency score
- source authority
- predicted action probabilities
- final score

### 13.3 User Profile State

- top weighted interests
- top weighted skills
- current freshness preference effects

This makes profile adaptation and timeliness trade-offs visible.

---

## 14. Advantages of the news version

Compared with a generic content ranker, this algorithm:

1. models preference strength instead of only tag presence
2. preserves separate topic and skill influence
3. reacts inside the session
4. adapts from feedback in real time
5. expands beyond onboarding
6. promotes the most current personally relevant news instead of only globally trending news

---

## 15. Implementation summary

The implemented news system includes:

- weighted student profiles
- news-only cards with freshness, urgency, authority, and actionability features
- weighted retrieval over onboarding, behavior, embeddings, exploration, and trending
- real-time profile updates from feedback
- processed ranker rows aligned with news engagement labels

This algorithm is a weighted, online, X-style recommendation system adapted for a student news feed where the most relevant fresh news should surface first.
