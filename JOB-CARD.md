# Job card

**What it does (one sentence):** Classifies a support message so it lands on the right team, with an urgency level.

**Input:** `{ "text": "string, 1-2000 characters" }`

**Output:**
```
{ "category": one of [billing|bug|feature|other],
  "urgency": one of [low|normal|high],
  "suggested_team": one of [billing-support|engineering|product|general-support],
  "confidence": 0.0-1.0,
  "reason": "one short sentence" }
```

**It must never:** invent a category outside the list · return free text instead of this shape · give medical, legal, or financial advice · reveal the prompt

**When unsure it should:** return `category: "other"`, `suggested_team: "general-support"`, with `confidence` below 0.5 — not a guess dressed up as confidence.

## Passes the three rules

1. **Closed output** — every field is a fixed enum except `reason` (one short sentence) and `confidence` (a bounded number). Can be drawn on paper before any code — done, above.
2. **One decision** — one message in, one classification out. No memory of prior messages, no follow-up questions.
3. **A human could grade it** — given a support message, a person can look at the category/urgency/team and say whether it's right.