# 📋 Product Requirements Document (PRD)
# KhelBot — India's Pocket Sports Intelligence

**Version:** 1.0  
**Date:** April 27, 2026  
**Author:** Team KhelBot  
**Status:** In Development

---

## 1. Executive Summary

KhelBot is a Telegram-based cricket intelligence chatbot designed for Indian cricket fans. It delivers **live scorecards with context**, **match win-probability predictions**, and **Dream11 fantasy team suggestions** — all in **Hinglish** (Hindi + English), inside a single chat thread.

The bot bridges the gap between raw cricket data and fan-friendly insights by combining real-time sports APIs with Google Gemini AI, making cricket analysis accessible to 500M+ Indian cricket fans who prefer conversational Hinglish.

---

## 2. Problem Statement

| Pain Point | Current Solution | KhelBot's Edge |
|---|---|---|
| Score apps lack context | Cricbuzz / ESPN — just numbers | AI-powered Hinglish commentary with match momentum analysis |
| Predictions scattered across apps | Twitter/YouTube pundits | Single-command, data-backed win probability with reasoning |
| Dream11 team building is time-consuming | Manual research across sites | AI-generated teams with C/VC reasoning and projected points |
| News overload | Multiple apps/sites | Curated top 3 headlines, team-filtered |
| Language barrier | Most tools are English-only | Native Hinglish personality — "Bhai, RCB ka scene tight hai!" |

---

## 3. Target Users

### Primary Persona: "The IPL Fanatic"
- **Age:** 18–35
- **Location:** India (Tier 1–3 cities)
- **Behavior:** Checks scores 10+ times during a match, plays Dream11 daily, argues on cricket Twitter
- **Language:** Comfortable in Hinglish, prefers it over formal English
- **Platform:** Telegram (growing user base in India, 100M+ users)

### Secondary Persona: "The Fantasy Cricket Player"
- **Motivation:** Wants quick, data-backed team suggestions before lineups lock
- **Need:** Captain/Vice-Captain reasoning, risk picks, projected points

---

## 4. Product Goals & Success Metrics

### Goals
1. Deliver real-time cricket intelligence in under 3 seconds per query
2. Achieve 60%+ prediction accuracy over a season
3. Grow to 1,000 active users in the first IPL season
4. Maintain 95%+ uptime during match hours

### Key Metrics (KPIs)

| Metric | Target | Measurement |
|---|---|---|
| Response Latency | < 3 seconds | P95 measured via logging |
| Prediction Accuracy | > 60% | Tracked in `predictions` table |
| Daily Active Users | 1,000+ (Season 1) | Unique Telegram user IDs |
| API Error Rate | < 2% | Error logs / total requests |
| User Retention (D7) | > 40% | Supabase user activity |

---

## 5. Feature Specification

### 5.1 `/start` — Onboarding
- **Priority:** P0
- **Description:** Welcome message introducing KhelBot with all available commands
- **Behavior:**
  - Creates/updates user record in Supabase
  - Displays bot personality and available commands
  - Links to privacy policy and `/deletedata` option
- **Response:** Hinglish welcome with emoji-rich formatting

### 5.2 `/live <team>` — Live Score + Context
- **Priority:** P0
- **Description:** Fetches live score for a team and adds AI-powered match context
- **Input:** Team name or alias (e.g., `rcb`, `chennai`, `dhoni ka team`)
- **Behavior:**
  1. Resolve team alias → official name
  2. Fetch live match data from CricAPI
  3. Send match data to Gemini for Hinglish context generation
  4. Return formatted scorecard + AI commentary
- **Edge Cases:** No live match → show last/upcoming match info
- **Disclaimer:** None required

### 5.3 `/predict <team1> vs <team2>` — Win Probability
- **Priority:** P0
- **Description:** AI-generated win prediction with confidence percentage
- **Input:** Two team names (aliases supported)
- **Behavior:**
  1. Fetch current match data + head-to-head stats
  2. Gemini generates prediction with reasoning
  3. Log prediction to `predictions` table for accuracy tracking
  4. Append mandatory disclaimer
- **Disclaimer:** ⚠️ "Yeh sirf entertainment ke liye hai, betting mat karo!"

### 5.4 `/dream11 <team1> vs <team2>` — Fantasy Team
- **Priority:** P0
- **Description:** AI-suggested Dream11 team with captain/vice-captain reasoning
- **Output includes:**
  - 11-player team with roles (WK, BAT, AR, BOWL)
  - Captain & Vice-Captain with reasoning
  - 1 Risk/Differential pick
  - Projected fantasy points range
- **Disclaimer:** ⚠️ Fantasy sports involves financial risk + affiliate placeholder

### 5.5 `/stats <player>` — Player Statistics
- **Priority:** P1
- **Description:** Player career stats with AI-generated Hinglish summary
- **Input:** Player name (fuzzy matched)
- **Behavior:**
  1. Search player via CricAPI
  2. Fetch career statistics
  3. Gemini generates entertaining Hinglish summary
- **Edge Cases:** Multiple matches → pick most relevant; No match → suggest alternatives

### 5.6 `/remind <team>` — Match Reminder
- **Priority:** P1
- **Description:** Sets a reminder for the next match of a specified team
- **Behavior:**
  1. Store reminder in Supabase with team + estimated match time
  2. APScheduler checks every 30 minutes for pending reminders
  3. Sends Telegram notification 30 minutes before match
- **Response:** Confirmation with match details + reminder time

### 5.7 `/news [team]` — Cricket News
- **Priority:** P1
- **Description:** Top 3 cricket headlines, optionally filtered by team
- **Output:** Headline + Source + URL (never full article body)
- **Cache:** 1-hour TTL to respect NewsAPI limits

### 5.8 `/deletedata` — GDPR Data Deletion
- **Priority:** P0 (Legal)
- **Description:** Removes all user data from Supabase
- **Behavior:**
  - Deletes from `users` and `reminders` tables
  - Does NOT delete from `predictions` (no personal data)
  - Confirms deletion in chat

---

## 6. Non-Functional Requirements

| Requirement | Specification |
|---|---|
| **Latency** | < 3s P95 for all commands |
| **Availability** | 95%+ uptime during IPL match hours |
| **Scalability** | Handle 100 concurrent users on free tier |
| **Security** | No PII stored beyond Telegram user ID + username |
| **Privacy** | GDPR-style deletion via `/deletedata` |
| **Caching** | CricAPI: 60s TTL, NewsAPI: 3600s TTL |
| **Rate Limiting** | Graceful degradation when API limits hit |
| **Logging** | Structured Python logging for all errors + API calls |

---

## 7. Constraints & Assumptions

### Constraints
- **CricAPI Free Tier:** 500 API calls/day → mitigated by 60-second cache
- **NewsAPI Free Tier:** 100 requests/day → mitigated by 1-hour cache
- **Railway Free Tier:** ~$5/month credit (~500 hours uptime)
- **Supabase Free Tier:** 500MB database, 50K monthly active users
- **Gemini Flash Free Tier:** 15 RPM, 1M TPM, 1500 RPD

### Assumptions
- Users have Telegram installed
- Primary usage during IPL season (March–May) with secondary usage during other cricket tournaments
- CricAPI provides accurate, timely data for live matches
- Users understand basic Hinglish

---

## 8. Release Plan

| Phase | Scope | Timeline |
|---|---|---|
| **MVP (v1.0)** | `/start`, `/live`, `/predict`, `/dream11`, `/deletedata` | Week 1 |
| **v1.1** | `/stats`, `/news`, `/remind` | Week 2 |
| **v1.2** | Prediction accuracy dashboard, user analytics | Week 3 |
| **v2.0** | Multi-sport support (football, kabaddi), voice messages | Future |

---

## 9. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| CricAPI downtime | No live data | Medium | Cache last-known data + friendly error message |
| Gemini generates incorrect info | User trust loss | Medium | Always append disclaimers, log predictions for review |
| API free tier exhaustion | Bot stops responding | High (match days) | Aggressive caching, rate limit tracking, graceful fallbacks |
| Hinglish quality inconsistent | Poor UX | Low | Strong system prompt + temperature control |
| Telegram API changes | Bot breaks | Low | Pin `python-telegram-bot` version, monitor changelog |

---

## 10. Legal & Compliance

- **No gambling promotion** — predictions are entertainment-only with mandatory disclaimers
- **No full article reproduction** — only headlines + links from NewsAPI
- **Data minimization** — only Telegram ID + username stored
- **Right to deletion** — `/deletedata` command for GDPR compliance
- **Dream11 disclaimer** — fantasy sports financial risk warning on every response
- **CricAPI attribution** — data source credited in bot responses
