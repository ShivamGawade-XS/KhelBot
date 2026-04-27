# 🔧 Tech Stack — KhelBot

**Version:** 1.0 | **Date:** April 27, 2026

---

## Core Runtime

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.11+ | Primary language — async support, rich ecosystem |
| **python-telegram-bot** | 20.7 | Telegram Bot API wrapper with async handlers |

---

## External APIs

| Service | Plan | Purpose | Rate Limits |
|---|---|---|---|
| **CricAPI** | Free | Live scores, match info, player stats | 500 calls/day |
| **Google Gemini** | Free (AI Studio) | AI-powered Hinglish commentary & predictions | 15 RPM, 1500 RPD |
| **NewsAPI** | Free (Developer) | Cricket news headlines | 100 requests/day |
| **Supabase** | Free | PostgreSQL database (users, reminders, predictions) | 500MB, 50K MAU |

---

## Python Dependencies

| Package | Version | Purpose |
|---|---|---|
| `python-telegram-bot` | 20.7 | Telegram bot framework |
| `google-generativeai` | 0.8.3 | Google Gemini AI SDK |
| `httpx` | 0.27.0 | Async HTTP client for CricAPI & NewsAPI |
| `supabase` | 2.9.1 | Supabase Python client |
| `python-dotenv` | 1.0.1 | Environment variable management |
| `apscheduler` | 3.10.4 | Scheduled jobs (match reminders) |
| `pytest` | 8.3.4 | Unit testing framework |
| `pytest-asyncio` | 0.24.0 | Async test support |

---

## Infrastructure & Deployment

| Component | Choice | Rationale |
|---|---|---|
| **Hosting** | Railway | Free tier ($5/month credit), Python native, easy env vars |
| **Database** | Supabase PostgreSQL | Free tier, REST API, built-in auth (not needed here) |
| **Cache** | In-memory (Python dict) | Zero infra cost, sufficient for <100 concurrent users |
| **CI/CD** | Railway auto-deploy | Auto-deploys on `git push` to `main` branch |
| **Monitoring** | Railway logs + Python logging | Structured logs with severity levels |

---

## Development Tools

| Tool | Purpose |
|---|---|
| **Git** | Version control |
| **GitHub** | Repository hosting |
| **VS Code** | IDE |
| **Postman** | API testing |
| **Telegram BotFather** | Bot creation & token management |

---

## Architecture Decisions

### Why Python?
- Largest ecosystem for AI/ML integrations (Gemini SDK is Python-first)
- `python-telegram-bot` is the most mature Telegram bot framework
- Async support via `asyncio` handles concurrent users well

### Why Telegram (not WhatsApp/Discord)?
- **No business verification** needed (WhatsApp requires it)
- **Bot API is free** and full-featured
- **100M+ Indian users** and growing
- **Rich formatting** (Markdown, inline buttons)
- **Group support** for cricket fan communities

### Why Gemini Flash (not GPT-4/Claude)?
- **Free tier** is the most generous (1500 RPD vs OpenAI's limited free)
- **Fastest inference** among frontier models
- **Sufficient quality** for sports commentary (not writing research papers)
- **Google ecosystem** synergy

### Why Supabase (not Firebase/MongoDB)?
- **PostgreSQL** — proper relational DB for structured sports data
- **Free tier** is generous (500MB)
- **REST API** auto-generated — no ORM needed
- **RPC functions** for complex queries (prediction accuracy)

### Why In-Memory Cache (not Redis)?
- **Zero cost** — no additional infrastructure
- **Sufficient** for <100 concurrent users
- **Sports data is ephemeral** — cache loss on restart is acceptable
- **Simple interface** — `get()`, `set()`, `invalidate()`

---

## API Integration Map

```
KhelBot
  │
  ├── CricAPI (cricapi.com)
  │   ├── GET /currentMatches     → Live scores
  │   ├── GET /match_info?id=x    → Match details
  │   └── GET /players?search=x   → Player search
  │
  ├── Google Gemini (AI Studio)
  │   └── POST /generateContent   → AI commentary
  │       ├── Prompt 1: Live context
  │       ├── Prompt 2: Predictions
  │       ├── Prompt 3: Dream11 teams
  │       └── Prompt 4: Player summaries
  │
  ├── NewsAPI (newsapi.org)
  │   └── GET /everything?q=x     → Headlines
  │
  └── Supabase (supabase.co)
      ├── REST /users              → CRUD
      ├── REST /reminders          → CRUD
      ├── REST /predictions        → CRUD
      └── RPC  /increment_query_count → Functions
```

---

## Environment Variables

| Variable | Source | Required |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | BotFather | ✅ |
| `CRICAPI_KEY` | cricapi.com | ✅ |
| `GEMINI_API_KEY` | AI Studio | ✅ |
| `SUPABASE_URL` | Supabase Dashboard | ✅ |
| `SUPABASE_KEY` | Supabase Dashboard | ✅ |
| `NEWSAPI_KEY` | newsapi.org | ✅ |
