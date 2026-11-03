<p align="center">
  <img src="https://img.shields.io/badge/🏏-KhelBot_V4-e94560?style=for-the-badge&labelColor=1a1a2e" alt="KhelBot"/>
</p>

<h1 align="center">KhelBot 🏏</h1>
<h3 align="center">India ka Apna Production-Grade Cricket Intelligence Bot</h3>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/telegram-bot-26A5E4?style=flat-square&logo=telegram&logoColor=white" />
  <img src="https://img.shields.io/badge/meta-llama_3.3_70b-4285F4?style=flat-square&logo=meta&logoColor=white" />
  <img src="https://img.shields.io/badge/duckduckgo-real_time_search-DE5833?style=flat-square&logo=duckduckgo&logoColor=white" />
  <img src="https://img.shields.io/badge/supabase-postgresql-3ECF8E?style=flat-square&logo=supabase&logoColor=white" />
  <img src="https://img.shields.io/badge/tests-54_passing-brightgreen?style=flat-square" />
</p>

<p align="center">
  Live scores with AI commentary • Real predictions • Dream11 fantasy teams • 100% Real-time Web Search • All in Hinglish 🇮🇳
</p>

---

## ⚡ What is KhelBot V4?

KhelBot is a production-grade Telegram chatbot giving Indian cricket fans live intelligence powered by **real-time internet search** and **Meta Llama 3.3 (via Groq)**:

- 🏏 **Live Scores & AI Commentary** — Real-time ball-by-ball scorecards with Hinglish AI takes.
- 🔮 **Match Predictions** — Win probabilities with key factors and automatic result tracking.
- 🏆 **Dream11 Fantasy Teams** — Captain/Vice-Captain recommendations based on real current form.
- 📋 **Playing 11 & Pitch Reports** — Live pitch conditions, toss factors, and probable/confirmed lineups.
- 📊 **Player Statistics & Head-to-Head** — Deep career statistics with AI summaries and side-by-side face-offs.
- ⏰ **Smart Match Reminders** — Synced with real CricAPI fixtures (alerts sent 30 mins before match).
- 💬 **Banter & Roast** — Savage Hinglish roast engine and interactive trivia quiz.

---

## 🚀 Commands Directory

| Command | Description | Example |
|---|---|---|
| `/start` | Onboarding & interactive quick buttons | `/start` |
| `/today` | 📺 Today's matches & timings | `/today` |
| `/live <team>` | 🏏 Live score + AI commentary | `/live rcb` |
| `/playing11 <match>` | 📋 Playing 11 & Lineups | `/playing11 csk vs mi` |
| `/pitch <match>` | 🏟️ Pitch & weather analysis | `/pitch rcb vs kkr` |
| `/predict <t1> vs <t2>` | 🔮 Match win probability | `/predict csk vs mi` |
| `/dream11 <t1> vs <t2>` | 🏆 Fantasy team suggestion | `/dream11 kkr vs pbks` |
| `/stats <player>` | 📊 Player statistics | `/stats virat kohli` |
| `/h2h <t1> vs <t2>` | ⚔️ Head-to-head records | `/h2h mi vs csk` |
| `/compare <p1> vs <p2>` | 🔄 Player comparison | `/compare kohli vs rohit` |
| `/schedule [team]` | 📅 Upcoming matches | `/schedule csk` |
| `/points` | 🏅 IPL points table | `/points` |
| `/orangecap` | 🧡 Orange Cap race | `/orangecap` |
| `/purplecap` | 💜 Purple Cap race | `/purplecap` |
| `/ask <query>` | 💬 Freeform cricket question | `/ask who hit longest six in IPL?` |
| `/quiz` | 🧠 Cricket trivia quiz (Inline buttons) | `/quiz` |
| `/roast <team>` | 🔥 Savage comedy roast | `/roast rcb` |
| `/recap <team>` | 📝 Recent match summary | `/recap mi` |
| `/trending` | 🔥 Trending cricket news | `/trending` |
| `/poll <t1> vs <t2>` | 📊 Telegram prediction poll | `/poll csk vs mi` |
| `/accuracy` | 📈 Verified prediction stats | `/accuracy` |
| `/remind <team>` | ⏰ Match reminder (30m prior) | `/remind rcb` |
| `/news [team]` | 📰 Top cricket headlines | `/news` |
| `/favteam <team>` | ⭐ Set your favorite team | `/favteam csk` |
| `/deletedata` | 🗑️ Delete your data (GDPR/DPDP) | `/deletedata` |
| `/help` | ❓ Full command list | `/help` |

---

## 🏗️ Production Architecture & Safeguards

```
                     ┌──────────────────────────────────────────────┐
                     │          Telegram Cloud Servers              │
                     └──────────────────────┬───────────────────────┘
                                            │ Long Polling (HTTPS)
                                            ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ KHEL-BOT PRODUCTION ENGINE                                                      │
│                                                                                  │
│   ┌───────────────────────────┐         ┌──────────────────────────────────────┐ │
│   │ Keep-Alive & Health Check │         │ python-telegram-bot (AsyncIO)        │ │
│   │ Flask (Port 8080)         │         │ ├─ UserRateLimiter (Token Bucket)    │ │
│   │ ├─ GET /                  │         │ ├─ Automatic Message Chunking        │ │
│   │ └─ GET /health            │         │ ├─ PII/Token Redacting Logger        │ │
│   └───────────────────────────┘         │ └─ Centralized safe_reply Handler    │ │
│                                         └──────────────────┬───────────────────┘ │
│                                                            │                     │
│               ┌────────────────────────────────────────────┴─────────────┐       │
│               ▼                                                          ▼       │
│   ┌─────────────────────────────┐                    ┌─────────────────────────┐ │
│   │ Real-Time Services          │                    │ Bounded Storage Layer   │ │
│   │ ├─ Groq Llama-3.3-70B       │                    │ ├─ Thread-Safe TTLCache │ │
│   │ ├─ Cached DDGS Search       │                    │ │  (Max 2000 Keys, LRU) │ │
│   │ ├─ CricAPI Match Client     │                    │ └─ Async Supabase Client│ │
│   │ └─ NewsAPI Client           │                    │    (Non-blocking thread)│ │
│   └───────────────┬─────────────┘                    └────────────┬────────────┘ │
└───────────────────┼───────────────────────────────────────────────┼──────────────┘
                    ▼                                               ▼
         ┌─────────────────────┐                         ┌─────────────────────┐
         │ External Providers  │                         │ Supabase PostgreSQL │
         │ ├─ Groq Cloud       │                         │ ├─ users            │
         │ ├─ DuckDuckGo Web   │                         │ ├─ reminders        │
         │ ├─ CricAPI / NewsAPI│                         │ └─ predictions      │
         └─────────────────────┘                         └─────────────────────┘
```

### Key Engineering Upgrades:
1. **Non-Blocking Async Execution:** All database queries execute via non-blocking asynchronous wrappers (`asyncio.wait_for(asyncio.to_thread(...))`), preventing event-loop starvation.
2. **Per-User Token Bucket Rate Limiter:** Protects upstream APIs with a 15 req/min window and a 1.5s rapid-fire cooldown.
3. **Thread-Safe LRU-Bounded Cache:** In-memory `TTLCache` protected by `threading.RLock()` with 2,000 maximum key bounds to avoid memory leaks.
4. **Server-Side Quiz Verification:** Eliminates client-side answer leaking in button callback data.
5. **Real-Time Prediction Resolution Engine:** Automatically compares match results from CricAPI against logged predictions and records verified accuracy.
6. **Smart Fixture-Based Reminders:** Calculates actual upcoming fixture start times instead of mock offsets.
7. **PII and Secret Redaction:** Built-in logging filter automatically masks bot tokens, API keys, and Telegram user IDs.

---

## ⚡ Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/ShivamGawade-XS/KhelBot.git
cd KhelBot
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate    # Linux/macOS
pip install -r requirements.txt
```

### 2. Configure Environment (.env)
```bash
cp .env.example .env
```
Fill in your API keys in `.env`:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
CRICAPI_KEY=your_cricapi_key
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
NEWSAPI_KEY=your_newsapi_key
```

### 3. Initialize Database
Execute the SQL in `database/schema.sql` inside your Supabase SQL Editor.

### 4. Run Tests & Start Bot
```bash
pytest
python main.py
```

---

## 🐳 Docker Deployment
```bash
docker build -t khelbot .
docker run -p 8080:8080 --env-file .env khelbot
```

---

## 📄 License
Open source under the [MIT License](LICENSE).
Made with ❤️ and 🏏 for Indian cricket fans!
