# 🏗️ Design Document — KhelBot

**Version:** 1.0 | **Date:** April 27, 2026 | **Status:** In Development

---

## 1. System Overview

KhelBot is a Python-based Telegram bot that orchestrates data from multiple external APIs, processes it through Google Gemini AI, and delivers contextual cricket intelligence in Hinglish.

```
  Telegram Users
       │
       ▼
  Telegram Bot API
       │
       ▼
┌──────────────────────────────────┐
│         KHELBOT CORE             │
│  Handlers → Services → Database │
│              ↕                   │
│           Utilities              │
└──────┬────────┬────────┬─────────┘
       ▼        ▼        ▼
   CricAPI   Gemini   Supabase
              ↕
           NewsAPI
```

---

## 2. Layered Architecture

| Layer | Responsibility | Dependencies |
|---|---|---|
| **Handlers** | Parse commands, orchestrate flow, format responses | Services, Database, Utils |
| **Services** | External API communication, AI generation, caching | Config, Cache |
| **Database** | Supabase CRUD operations | Config |
| **Utilities** | Logging, input validation, output formatting | None |
| **Config** | Environment variable loading & validation | None |

**Why Layered?** Separation of concerns, independent testability, API changes isolated to service layer, new commands = new handler file.

---

## 3. Data Flow — Key Commands

### `/live <team>`
1. Extract args → resolve alias via `validators.py`
2. Fetch live data → `cricapi.get_match_by_team()`
3. Format score → `formatters.format_score()`
4. Generate Hinglish context → `gemini.generate_live_context()`
5. Combine & send

### `/predict <team1> vs <team2>`
1. Parse two teams → resolve aliases
2. Fetch match data → CricAPI
3. Generate prediction → Gemini (with confidence %)
4. Log to `predictions` table
5. Append disclaimer & send

### `/dream11 <team1> vs <team2>`
1. Parse teams → fetch match data
2. Generate fantasy team → Gemini (C/VC, risk pick, projected points)
3. Append disclaimer + affiliate placeholder & send

---

## 4. Database Schema (Supabase PostgreSQL)

### `users`
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    favorite_team TEXT,
    query_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `reminders`
```sql
CREATE TABLE reminders (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL REFERENCES users(telegram_id),
    team_name TEXT NOT NULL,
    match_id TEXT,
    remind_at TIMESTAMPTZ NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `predictions`
```sql
CREATE TABLE predictions (
    id BIGSERIAL PRIMARY KEY,
    match_id TEXT NOT NULL,
    match_name TEXT NOT NULL,
    predicted_winner TEXT NOT NULL,
    confidence_pct REAL NOT NULL,
    actual_winner TEXT,
    is_correct BOOLEAN,
    match_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### DB Functions
- `increment_query_count(uid)` — bumps user query count
- `get_prediction_accuracy()` — returns total, correct, accuracy %

---

## 5. Caching Strategy

In-memory TTL dictionary cache (no Redis needed for free tier scale).

| Source | TTL | Rationale |
|---|---|---|
| CricAPI live scores | 60s | Scores update every ball (~30s) |
| CricAPI player stats | 300s | Stats don't change mid-match |
| NewsAPI | 3600s | News cycles are hourly |
| Gemini | Not cached | Responses should be contextually fresh |

---

## 6. AI Integration — Gemini

- **Model:** `gemini-1.5-flash` (fast, generous free tier)
- **Temperature:** 0.7
- **System prompt:** Hinglish cricket buddy personality
- **All calls** wrapped in try/except with Hinglish fallbacks

| Command | Max Tokens | Disclaimer |
|---|---|---|
| `/live` | 500 | No |
| `/predict` | 500 | Yes — gambling warning |
| `/dream11` | 700 | Yes — financial risk |
| `/stats` | 400 | No |

---

## 7. Error Handling

Every error surfaces as a friendly Hinglish message:

| Scenario | Message |
|---|---|
| No live match | "Abhi koi live match nahi chal raha. Agli match ka wait karo! 🏏" |
| API down | "API wale bhi chai break pe hain ☕ Thodi der mein try karo!" |
| Invalid team | "Yeh team toh humne nahi suni bhai 🤔 /start se valid teams dekh lo!" |
| Unknown error | "Kuch toh gadbad hai Daya! 🕵️ Thodi der mein aana!" |

---

## 8. Security

| Concern | Mitigation |
|---|---|
| Key exposure | `.env` + `.gitignore` |
| SQL injection | Supabase parameterized queries |
| Input abuse | `sanitize_input()` strips special chars |
| Data privacy | Only telegram_id + username stored |
| GDPR | `/deletedata` removes all personal data |

---

## 9. Deployment (Railway)

- **Platform:** Railway (free tier, $5/month)
- **Runtime:** Python 3.11+
- **Mode:** Long polling (no webhook setup needed)
- **Procfile:** `web: python main.py`
- **Env vars:** Set in Railway dashboard
