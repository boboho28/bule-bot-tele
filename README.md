# tv-signal-bot

A webhook-based bot that receives trading alerts and sends them to Telegram.

## Deployment

- Render will use `gunicorn main:app` to start the bot.
- Make sure your `config.py` contains the right `BOT_TOKEN` and `CHAT_ID`.

## Required Environment Variables

- BOT_TOKEN
- CHAT_ID
