# Morning Briefs

> Automated daily voice briefing delivered at 08:00 CET via Telegram

## Overview

A personal morning briefing system that generates a ~90-second audio summary of your day, delivered as a Telegram voice message every weekday at 08:00 CET.

**Cost**: ~0.015 EUR/day (OpenAI TTS)
**Delivery**: Telegram voice message
**Schedule**: Weekdays only, 08:00 CET

---

## Content Structure

The briefing follows this order (~90 seconds total):

1. **Weather** (15s) - 3-day outlook, relevant alerts (rain, extreme temps)
2. **Calendar** (20s) - Today + tomorrow events, travel time buffers
3. **Task Summary** (30s) - High-priority items from Notion (Ultimate Brain)
4. **Proactive Suggestion** (25s) - One context-aware, high-impact suggestion

**Tone**: Warm, concise, actionable
**Voice**: OpenAI TTS - test both `alloy` and `nova` for preference

---

## Technical Architecture

### Data Sources

| Source | API | Auth | Cost |
|--------|-----|------|------|
| Weather | wttr.in | None (free) | Free |
| Calendar | Google Calendar API | OAuth2 | Free |
| Tasks | Notion API | Bearer token | Free |
| Voice | OpenAI TTS | API key | ~$0.015/briefing |

### Stack

- **Language**: Python
- **TTS**: OpenAI TTS API (`tts-1` model, `alloy` or `nova` voice)
- **Delivery**: Telegram Bot API (send voice message)
- **Scheduler**: Windows Task Scheduler / cron
- **Output**: MP3 file -> Telegram voice message

### Script Flow

```
1. Fetch weather from wttr.in (no API key needed)
2. Fetch today's calendar from Google Calendar API
3. Query Notion for high/medium priority tasks (Status=To Do)
4. Generate proactive suggestion (rule-based + optional LLM assist)
5. Compose text script from templates
6. Call OpenAI TTS API to generate MP3
7. Send MP3 via Telegram Bot API
8. Log result to briefing log
```

---

## Implementation Phases

### Phase 1: Content Design
- Define briefing text templates
- Test content quality with sample data
- Finalize tone and structure

### Phase 2: Technical Setup
- Set up Telegram bot
- Configure Google Calendar API OAuth2
- Wire up Notion API queries
- Integrate OpenAI TTS
- Build the orchestration script

### Phase 3: Automation
- Set up cron/Task Scheduler for 08:00 CET weekdays
- Script location: project folder
- Logging: daily log files
- Error handling: fallback to text if TTS fails

### Phase 4: Validation (2 weeks)
- Week 1: Manual trigger, review content quality
- Week 2: Auto-trigger, gather feedback
- Adjust timing, content length, tone

---

## Iteration Ideas

- Weekend/holiday variants (lighter content)
- Context-aware suggestions based on calendar density
- Dynamic length (skip empty sections)
- Weekly summary briefing on Mondays
- Integration with habit tracking

---

## Dependencies

- OpenAI API key (for TTS)
- Telegram Bot token
- Google Calendar OAuth2 credentials
- Notion API key (already have)

---

## Notes

- Captured from session 2026-01-29
- Status: Parked for future implementation
- Priority to be defined
