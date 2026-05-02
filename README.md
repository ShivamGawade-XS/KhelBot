<p align="center">
  <img src="https://img.shields.io/badge/🏏-KhelBot-e94560?style=for-the-badge&labelColor=1a1a2e" alt="KhelBot"/>
</p>

<h1 align="center">KhelBot 🏏</h1>
<h3 align="center">India ka Apna Cricket Intelligence Bot</h3>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/telegram-bot-26A5E4?style=flat-square&logo=telegram&logoColor=white" />
  <img src="https://img.shields.io/badge/gemini-1.5_flash-4285F4?style=flat-square&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/supabase-database-3ECF8E?style=flat-square&logo=supabase&logoColor=white" />
  <img src="https://img.shields.io/badge/railway-deployed-0B0D0E?style=flat-square&logo=railway&logoColor=white" />
</p>

<p align="center">
  Live scores with AI context • Win predictions • Dream11 teams • All in Hinglish 🇮🇳
</p>

---

## 🤔 What is KhelBot?

KhelBot is a **Telegram chatbot** that gives Indian cricket fans superpowers:

- 🏏 **Live Scores + Context** — Not just numbers, but AI-powered match commentary in Hinglish
- 🔮 **Match Predictions** — Data-backed win probability with reasoning
- 🏆 **Dream11 Teams** — AI-suggested fantasy teams with C/VC logic and risk picks
- 📊 **Player Stats** — Career stats with entertaining Hinglish summaries
- 📰 **Cricket News** — Top headlines, team-filtered
- ⏰ **Match Reminders** — Never miss your team's match

> **"Bhai, RCB ka scene tight hai! Kohli form mein hai aur pitch batting-friendly lag rahi hai. Win probability: 58% 🔥"** — KhelBot

---

## 🚀 Commands

| Command | Description | Example |
|---|---|---|
| `/start` | Onboarding + all commands | `/start` |
| `/live <team>` | Live score + AI context | `/live rcb` |
| `/predict <t1> vs <t2>` | Win prediction | `/predict csk vs mi` |
| `/dream11 <t1> vs <t2>` | Fantasy team suggestion | `/dream11 kkr vs pbks` |
| `/stats <player>` | Player statistics | `/stats virat kohli` |
| `/remind <team>` | Match reminder | `/remind mi` |
| `/news [team]` | Cricket headlines | `/news` or `/news rcb` |
| `/deletedata` | Delete your data (GDPR) | `/deletedata` |

### 🏷️ Team Aliases Supported

You can use short names, full names, or nicknames:

| Team | Accepted Aliases |
|---|---|
| Chennai Super Kings | `csk`, `chennai`, `dhoni`, `yellove` |
| Mumbai Indians | `mi`, `mumbai`, `rohit`, `paltan` |
| Royal Challengers Bengaluru | `rcb`, `bengaluru`, `bangalore`, `kohli` |
| Kolkata Knight Riders | `kkr`, `kolkata`, `knight riders` |
| And 6 more IPL teams... | See `utils/validators.py` for full list |

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│  Telegram   │────▶│   Handlers   │────▶│  Services  │
│  Users      │◀────│   Layer      │◀────│  Layer     │
└─────────────┘     └──────┬───────┘     └─────┬──────┘
                           │                    │
                    ┌──────▼───────┐     ┌──────▼──────┐
                    │  Database    │     │  External   │
                    │  (Supabase)  │     │  APIs       │
                    └──────────────┘     └─────────────┘
```

### Project Structure

```
khelbot/
├── main.py                 # Entry point
├── config/
│   └── settings.py         # Env var loader + validation
├── handlers/
│   ├── start.py            # /start command
│   ├── live.py             # /live command
│   ├── predict.py          # /predict command
│   ├── dream11.py          # /dream11 command
│   ├── stats.py            # /stats command
│   ├── remind.py           # /remind command
│   ├── news.py             # /news command
│   └── deletedata.py       # /deletedata command
├── services/
│   ├── cache.py            # In-memory TTL cache
│   ├── cricapi.py          # CricAPI integration
│   ├── gemini.py           # Google Gemini AI
│   └── newsapi.py          # NewsAPI integration
├── database/
│   ├── client.py           # Supabase client
│   ├── users.py            # User CRUD
│   ├── reminders.py        # Reminder CRUD
│   └── predictions.py      # Prediction CRUD
├── utils/
│   ├── logger.py           # Logging config
│   ├── validators.py       # Team aliases + input validation
│   └── formatters.py       # Output formatting
├── tests/
│   ├── test_live.py
│   ├── test_predict.py
│   └── test_formatters.py
├── docs/
│   ├── PRD.md              # Product requirements
│   ├── DESIGN.md           # System design
│   └── TECHSTACK.md        # Technology stack
├── .env.example
├── .gitignore
├── requirements.txt
├── Procfile
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Telegram account
- API keys (see below)

### 1. Clone the repo

```bash
git clone https://github.com/ShivamGawade-XS/KhelBot.git
cd KhelBot
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
TELEGRAM_BOT_TOKEN=your_token_from_botfather
CRICAPI_KEY=your_key_from_cricapi
GEMINI_API_KEY=your_key_from_ai_studio
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
NEWSAPI_KEY=your_key_from_newsapi
```

### 5. Set up Supabase database

Run the SQL from `docs/DESIGN.md` (Section 4) in your Supabase SQL Editor to create:
- `users` table
- `reminders` table
- `predictions` table
- `increment_query_count()` function
- `get_prediction_accuracy()` function

### 6. Run the bot

```bash
python main.py
```

### 7. Chat with your bot on Telegram!

Search for your bot username on Telegram and send `/start` 🚀

---

## 🔑 Getting API Keys

| Service | Where to Get | Free Tier |
|---|---|---|
| **Telegram Bot Token** | [BotFather](https://t.me/botfather) — `/newbot` | Unlimited |
| **CricAPI** | [cricapi.com](https://cricapi.com/) | 500 calls/day |
| **Gemini API** | [AI Studio](https://aistudio.google.com/apikey) | 15 RPM, 1500 RPD |
| **Supabase** | [supabase.com](https://supabase.com/) | 500MB DB |
| **NewsAPI** | [newsapi.org](https://newsapi.org/) | 100 req/day |

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

---

## 🚂 Deploying to Railway

1. Push your code to GitHub
2. Connect your repo to [Railway](https://railway.app/)
3. Add all 6 environment variables in Railway dashboard
4. Railway auto-deploys on every push to `main`

The `Procfile` is already configured:
```
worker: python main.py
```

---

## 📸 Screenshots

*Coming soon — bot is under active development!*

---

## ⚠️ Disclaimers

- **Predictions are for entertainment only** — KhelBot does NOT promote gambling
- **Dream11 suggestions involve financial risk** — play responsibly
- **News headlines are sourced from NewsAPI** — KhelBot does not create news content
- **Live data from CricAPI** — accuracy depends on upstream provider

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<p align="center">
  Made with ❤️ and 🏏 for Indian cricket fans
</p>
