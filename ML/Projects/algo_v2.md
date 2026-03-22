# Weighted Real-Time Recommendation Algorithm for Student Opportunity Feed

## 1. Purpose

This document describes the updated recommendation algorithm for the student opportunity feed.

The system extends the previous X-style architecture with:

- weighted interests
- weighted skills
- different influence strength for interests and skills
- real-time profile adaptation after each reaction to a card

The goal is not only to rank cards well, but also to continuously update the user profile while the user interacts with the feed.

---

## 2. Product behavior

The product shows one card at a time in a swipe-like recommendation feed.

Each card belongs to one of five pools:

1. hackathons
2. meetups
3. projects
4. courses
5. news

For every shown card, the user can react using one of the platform reactions:

- `open`
- `like`
- `share`
- `long_view`
- `skip_fast`
- `disengage`

After each reaction:

1. the interaction is saved
2. the user profile weights are updated
3. the next recommendation is recalculated

This makes the recommendation loop online and adaptive inside the session.

---

## 3. Core idea

The old logic treated selected onboarding interests and skills as mostly flat attributes.

The new logic treats them as weighted signals:

- each interest has its own weight
- each skill has its own weight
- skill weights can influence ranking stronger than interest weights
- reactions to cards change the weights of related interests and skills

This means that two users with the same set of interests and skills can still receive different feeds because their internal weights differ.

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

### 4.1 Interest weights

`interest_weights` is a mapping:

```json
{
  "ai": 1.42,
  "product": 1.18,
  "climate": 0.84
}
```

### 4.2 Skill weights

`skill_weights` is a mapping:

```json
{
  "python": 1.51,
  "analytics": 1.34,
  "react": 0.72
}
```

### 4.3 Why separate weights matter

Interests and skills represent different concepts:

- interests describe what the student wants to explore
- skills describe what the student can apply or wants to strengthen

For ranking, skills should usually be more predictive of opportunity fit than interests alone.

Therefore, the algorithm gives them different influence in retrieval and scoring.

---

## 5. Request context

For each feed request, the system builds a request context containing:

### 5.1 User profile fields

- weighted interests
- weighted skills
- experience level
- preferred language
- region
- preferred formats

### 5.2 Behavioral fields

- recently viewed cards
- recently liked cards
- recently shared cards
- recently opened cards
- skipped cards
- dwell time statistics
- per-pool engagement

### 5.3 Session fields

- current session depth
- recent interaction streak
- time since last action
- novelty state
- diversity state

---

## 6. Candidate sourcing

The system keeps the X-style multi-source retrieval architecture, but now profile matching is weighted.

Each pool produces candidates independently:

- Hackathon Source
- Meetup Source
- Project Source
- Course Source
- News Source

Inside each pool, candidates can come from:

1. onboarding similarity retrieval
2. behavioral similarity retrieval
3. embedding retrieval
4. exploration retrieval
5. trending retrieval

### 6.1 Weighted onboarding retrieval

For each candidate card:

- card topics are compared with `interest_weights`
- card required skills are compared with `skill_weights`

Weighted onboarding score:

```text
OnboardingScore(card) =
  a1 * WeightedTopicMatch
+ a2 * WeightedSkillMatch
```

Where:

- `a1` = interest feature weight
- `a2` = skill feature weight
- `a2 > a1` in the current design

### 6.2 Weighted behavioral retrieval

The system builds temporary behavioral weight maps from previously engaged cards:

- topics from engaged cards increase behavioral topic affinity
- required and gained skills from engaged cards increase behavioral skill affinity

These behavioral maps are then used to retrieve cards similar to recent positive interactions.

### 6.3 Embedding retrieval

The user embedding is constructed from:

- weighted interests
- weighted skills
- recent interaction history

Skills contribute more strongly to the embedding than interests.

The candidate embedding comes from card metadata.

Candidates are retrieved by similarity between user and card embeddings.

---

## 7. Unified card schema

All cards are transformed into one rankable schema.

Core fields:

- `card_id`
- `card_type`
- `title`
- `short_description`
- `full_description`
- `topics`
- `skills_required`
- `skills_gained`
- `difficulty_level`
- `format`
- `language`
- `location`
- `start_date`
- `end_date`
- `application_deadline`
- `estimated_duration`
- `team_based`
- `host_organization`
- `cost_type`
- `reward_type`
- `eligibility_constraints`
- `freshness_timestamp`
- `quality_score`
- `popularity_score`
- `editorial_priority`
- `embedding_vector`

This allows all five pools to be ranked in one feed.

---

## 8. Hydration layer

After retrieval, candidate cards are enriched with ranking features.

### 8.1 Weighted user-card features

The new version computes weighted overlap features:

- `topic_overlap_score`
- `skill_overlap_score`
- `skill_gain_score`
- `interest_weight_mean`
- `skill_weight_mean`
- `interest_match_count`
- `skill_match_count`

### 8.2 Additional features

The pipeline also computes:

- `format_match`
- `language_match`
- `region_match`
- `difficulty_match`
- `opportunity_readiness_score`
- `novelty_score`
- `diversity_contribution`
- `similarity_to_recent_likes`
- `similarity_to_recent_skips`
- `mismatch_penalties`
- `embedding_alignment`

### 8.3 Readiness logic

Opportunity readiness is not based only on raw skill overlap.

It combines:

- weighted required skill match
- weighted skill gain compatibility

This helps recommend cards that are either immediately suitable or realistically useful for growth.

---

## 9. Filtering layer

Hard filters remove ineligible cards:

- expired deadline
- already ended event
- language mismatch when required
- geo mismatch for offline content
- inactive content
- low-integrity content
- recently shown duplicates

Soft filters reduce ranking chance:

- repeated pool exposure
- repeated organizer exposure
- low quality confidence
- low novelty

---

## 10. Ranking layer

The system remains multi-objective.

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
- mean profile weights
- match counts
- metadata features
- behavior aggregates
- diversity features
- session features

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
+ w8 * DiversityBoost
+ w9 * QualityBoost
- SoftFilterPenalty
```

---

## 11. Real-time profile adaptation

This is the main change in the new algorithm.

After each card reaction, the system updates user weights immediately.

### 11.1 Update principle

The card contains:

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

Interest updates and skill updates are not equal.

In the current design:

- skills are updated more aggressively than interests
- required skills are updated stronger than gained skills

This reflects the assumption that a reaction to a card is often a more direct signal about applicable skills than about broad curiosity alone.

### 11.4 Cold-start expansion

If a card contains a topic or skill not yet present in the user profile:

- it can be inserted into the profile
- it starts from a cold-start weight
- then future reactions can increase or decrease it

This allows the profile to evolve beyond onboarding.

### 11.5 Weight boundaries

To avoid instability, weights are clipped:

- minimum profile weight
- maximum profile weight

This prevents runaway growth or total collapse of a feature.

---

## 12. Real-time loop

The online loop for one session is:

1. build request context
2. retrieve candidates from all pools
3. hydrate candidates with weighted features
4. filter ineligible candidates
5. score candidates
6. assemble final feed
7. display top card
8. wait for user reaction
9. save interaction
10. update interest and skill weights
11. recompute next recommendation

This means recommendations are not static for the session.

They react immediately to what the user just did.

---

## 13. Display behavior

The interactive feed should show the recommendation in two clearly separated parts:

### 13.1 Card Content

- title
- type
- descriptions
- topics
- required skills
- gained skills
- metadata such as format, language, location, dates, cost, reward

### 13.2 Model Signals

- retrieval strategy
- retrieval reason
- retrieval similarity
- quality score
- novelty score
- diversity score
- predicted action probabilities
- final score

### 13.3 User Profile State

The interface should also display:

- top weighted interests
- top weighted skills

before and after reactions, so profile adaptation is observable.

---

## 14. Advantages of the new algorithm

Compared to the previous version, the updated system:

1. models preference strength instead of only presence or absence
2. distinguishes broad curiosity from actionable capability
3. allows session-level adaptation
4. updates the profile from feedback in real time
5. supports profile expansion beyond onboarding
6. makes future recommendations more responsive and personalized

---

## 15. Implementation summary

The implemented system includes:

- weighted user profile fields in the user dataset
- weighted overlap features in ranking
- weighted onboarding retrieval
- weighted behavioral retrieval
- embeddings built from weighted profiles
- real-time feedback updates for profile weights
- interactive recommendation loop with immediate recalculation

This algorithm is a weighted, online, X-style recommendation system adapted for a student opportunity platform.
