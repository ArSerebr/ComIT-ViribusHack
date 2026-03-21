# X-Style Recommendation Algorithm for Student Opportunity Feed

## 1. Purpose

This document describes a recommendation algorithm for a student platform using the architectural logic of the X recommendation system, adapted to our product context.

The platform recommends opportunities to students in a swipe-based feed. The feed contains different types of content cards:

- hackathons
- meetups
- projects
- courses
- news

The objective of the algorithm is:

- to personalize the feed based on onboarding data and behavioral feedback
- to rank cards from a shared multi-pool catalog
- to continuously adapt to user actions
- to optimize not for a single generic relevance score, but for multiple predicted actions

The system should preserve the structural logic of X:

- candidate sourcing
- hydration
- filtering
- scoring
- selection
- final feed assembly

but must be fully adapted to our platform, where there are no social subscriptions and no author-follow graph.

---

## 2. Product assumptions

### 2.1 User journey

A user enters the platform and passes onboarding.

During onboarding, the user selects:

- interests
- skills

After onboarding, the user sees a feed of content cards.

Each next card appears after the previous one is swiped.

Each card can be:

- liked
- shared
- opened by clicking into its detailed page

### 2.2 Content pools

All feed items belong to one of five global pools:

1. Hackathons
2. Meetups
3. Projects
4. Courses
5. News

There are no friend graphs, creator follow graphs, or subscription-based ranking sources in the core algorithm.

All recommendations are generated from the shared catalog of these five pools.

---

## 3. High-level architecture

The recommendation pipeline follows the X-style architecture:

1. **Request context building**
2. **Candidate retrieval from multiple pools**
3. **Hydration and feature enrichment**
4. **Filtering**
5. **Multi-objective scoring**
6. **Selection**
7. **Feed delivery**
8. **Online feedback loop**

In X, sources are built from in-network and out-of-network retrieval.  
In our case, sources are built from content pools and retrieval strategies, not from social relationships.

---

## 4. Core recommendation philosophy

The algorithm must not treat a user action as equal preference for all properties of the card.

Example problem:

If a user likes a hackathon card, it is incorrect to uniformly increase the preference for every attribute of that hackathon.  
The user may have liked it because of:

- topic
- difficulty
- location
- deadline proximity
- prize pool
- team format

but not because of all of them.

Therefore, the system should follow the X logic:

- predict multiple action probabilities separately
- combine them into a final ranking score
- update user preference representations through weighted signal attribution, not through naive full-card reinforcement

---

## 5. Request context building

When the feed request is generated, the system first builds a **request context**.

This context contains all relevant information needed for candidate retrieval and ranking.

### 5.1 Request context fields

#### User profile features
- selected interests from onboarding
- selected skills from onboarding
- declared experience level if available
- preferred content language if available
- country / region if available
- preferred formats if available:
  - online
  - offline
  - hybrid

#### Behavioral features
- recently viewed cards
- recently liked cards
- recently shared cards
- recently opened detail pages
- skipped cards
- dwell time per card if tracked
- recency-weighted interaction aggregates
- per-pool engagement statistics

#### Session features
- current session depth
- number of cards shown in this session
- recent interaction streak
- time since last action
- current device/platform if available

#### Exploration state
- exploration budget
- diversity quota status
- recent pool repetition counters
- novelty counters

---

## 6. Candidate sourcing layer

This layer replaces X’s social candidate sources with our own pool-based sources.

Each source independently proposes candidate cards.

The system then merges the candidates before ranking.

### 6.1 Candidate sources

We define five primary sources:

- Hackathon Source
- Meetup Source
- Project Source
- Course Source
- News Source

Each source retrieves candidate cards from its own pool.

### 6.2 Retrieval strategies inside each source

Each pool source may contain several retrieval sub-strategies.

#### Strategy A: onboarding similarity retrieval
Retrieve cards whose attributes match the user’s selected interests and skills.

#### Strategy B: behavioral similarity retrieval
Retrieve cards similar to previously engaged cards.

#### Strategy C: embedding retrieval
Retrieve cards whose vector representation is close to the current user embedding.

#### Strategy D: exploration retrieval
Retrieve novel or underexposed cards from the pool to avoid overfitting.

#### Strategy E: trending / high-quality retrieval
Retrieve globally strong candidates using platform-level quality signals.

### 6.3 Source outputs

Each source outputs a candidate set with metadata:

- card ID
- pool type
- retrieval strategy
- retrieval score
- retrieval reason
- lightweight eligibility flags

This matches the X philosophy where multiple candidate generators contribute items before deep ranking.

---

## 7. Retrieval model

The retrieval stage should be efficient and broad.

Its purpose is not to fully rank the feed, but to select a manageable set of potentially relevant cards.

### 7.1 User tower

The user tower encodes:

- onboarding interests
- onboarding skills
- recent interactions
- long-term interaction history
- pool preferences
- session context

Output:
- user embedding

### 7.2 Candidate tower

The candidate tower encodes each content card using its attributes.

Output:
- candidate embedding

### 7.3 Retrieval operation

For each feed request:

- compute or load the current user embedding
- fetch nearest candidates from each pool using embedding similarity
- combine with rule-based and metadata-based retrieval candidates
- produce a top-K candidate set for downstream ranking

This mirrors the X two-tower retrieval logic, but uses our five content pools instead of social content retrieval.

---

## 8. Unified card schema

To make all content types rankable in a single feed, every content entity must be transformed into a unified card format.

### 8.1 Core card schema

Each card should include:

- `card_id`
- `card_type`  
  (`hackathon`, `meetup`, `project`, `course`, `news`)
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
- `editorial_priority` if applicable
- `embedding_vector`

### 8.2 Optional type-specific attributes

#### Hackathon
- prize pool
- team size
- submission type
- domain focus
- sponsor tier

#### Meetup
- speaker quality
- event agenda density
- seats left
- networking relevance

#### Project
- role requirements
- project maturity
- expected commitment
- collaboration mode

#### Course
- certification
- pace
- duration
- prerequisite depth

#### News
- recency
- source authority
- topic urgency
- actionability relevance

This unified schema allows all five pools to be scored inside one ranking pipeline.

---

## 9. Hydration layer

After candidate retrieval, the system hydrates cards with richer features needed for filtering and ranking.

Hydration corresponds to X’s enrichment stage.

### 9.1 Hydrated information includes

#### Content-side enrichment
- full structured metadata
- normalized topic taxonomy
- normalized skill taxonomy
- location normalization
- freshness buckets
- quality features
- historical engagement rates
- content-type priors

#### User-card interaction features
- topic overlap score
- skill overlap score
- novelty score
- diversity contribution
- similarity to recently liked items
- similarity to recently skipped items
- mismatch penalties
- opportunity readiness score

#### Cross features
- user skill level vs card difficulty
- user interests vs card topic density
- user activity profile vs estimated time commitment
- user format preference vs card delivery format

---

## 10. Filtering layer

Before ranking, the system removes candidates that should not be shown.

This corresponds directly to X-style filter stages.

### 10.1 Hard filters

Hard filters remove cards that are ineligible.

Examples:

- expired application deadline
- event has ended
- unavailable in user language if language is required
- geo restriction
- hidden / inactive / low-integrity content
- duplicate entity already shown recently
- course unavailable in user region
- project closed to applicants
- malformed card metadata

### 10.2 Soft filters

Soft filters do not remove cards completely, but reduce their selection chance.

Examples:

- too many cards from the same pool recently
- too many cards with the same topic
- too many cards from the same organizer
- low freshness
- low quality confidence
- excessive repetition across sessions

---

## 11. Ranking layer

This is the central intelligence layer of the algorithm.

Like X, the system should not produce one generic relevance label only.  
Instead, it predicts probabilities of different user actions for each candidate.

### 11.1 Predicted actions

For each card, predict:

- `P(open)` — probability user opens the card detail page
- `P(like)` — probability user likes the card
- `P(share)` — probability user shares the card
- `P(long_view)` — probability user spends meaningful dwell time on the card
- `P(skip_fast)` — probability user skips quickly
- `P(disengage)` — probability card causes feed dissatisfaction or low-value interaction

Optional later additions:

- `P(apply)`
- `P(register)`
- `P(save)`
- `P(enroll)`

### 11.2 Ranking model inputs

The ranker should use:

- user embedding
- candidate embedding
- card metadata
- user-card overlap features
- short-term behavior history
- long-term preference aggregates
- session context
- diversity and novelty features
- per-pool calibration features

### 11.3 Ranking model architecture

Recommended architecture options:

#### MVP
- logistic regression per action
- gradient boosted trees per action
- CatBoost / LightGBM multi-head design

#### Later-stage
- transformer-based ranker
- sequential behavior encoder
- multi-task neural ranker

The ranking layer should remain candidate-independent in the X spirit:
a card is scored based on the user and context, not because of accidental batch neighbors.

---

## 12. Final score construction

Following X-style ranking, the final score is a weighted combination of predicted action probabilities.

### 12.1 Generic formula

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