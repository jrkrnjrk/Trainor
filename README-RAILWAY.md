# Rowboat on Railway (adapted)

This is an adapted copy of the archived [b1naryth1ef/rowboat](https://github.com/b1naryth1ef/rowboat) Discord moderation bot, prepared for deployment on [Railway](https://railway.app).

**Important limitations**
- Original project was archived in 2018 and written for Python 2.7 + the unmaintained `disco-py` library.
- Discord’s API has changed significantly (intents, API versions, etc.). The bot may not fully function without further code updates.
- This package focuses on making the deployment Railway-friendly (env vars, managed Postgres/Redis, config generation, Dockerfile).

## What was changed
- `Dockerfile` → Python 3.11, system deps, installs modern packages + tries to install disco/holster from git.
- `requirements.txt` → best-effort modern pins.
- `entrypoint.py` → generates `config.yaml` from environment variables, then starts bot / workers / web / all.
- `rowboat/sql.py` → prefers `DATABASE_URL` (Railway Postgres).
- `rowboat/redis.py` → prefers `REDIS_URL` (Railway Redis).
- `rowboat/__init__.py` → no longer crashes if `git` is missing or Sentry DSN is empty.
- `manage.py` → Python 3 print statements.
- `railway.toml` → basic Railway config.

## Railway setup

1. **Create a Railway project** and connect this folder (or push the contents to a GitHub repo and deploy from there).

2. **Add databases**
   - New → Database → PostgreSQL
   - New → Database → Redis

3. **Create the bot service** (from this repo/folder)
   - Variables (set these):
     - `DISCORD_TOKEN` = your bot token (from Discord Developer Portal)
     - `PROCESS` = `bot`   (or `all` to run bot + workers in one service)
     - `ENV` = `railway`
     - Reference `DATABASE_URL` from the Postgres service
     - Reference `REDIS_URL` from the Redis service
     - Optional: `SECRET_KEY`, `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET` (only needed for the web dashboard OAuth)
   - The start command is handled by the Dockerfile entrypoint (`python entrypoint.py`).

4. **Optional: separate workers service**
   - Same repo, set `PROCESS=workers`.

5. **Optional: web dashboard service**
   - Same repo, set `PROCESS=web`.
   - Railway will inject `PORT`. The entrypoint listens on it.
   - Generate a public domain if you want to access the dashboard.
   - You will also need Discord OAuth credentials and set the redirect URI.

6. **Deploy**
   - Railway builds the Dockerfile and starts the process.
   - Check the logs. The first run creates database tables via Peewee.

## Discord bot requirements
- Create an application at https://discord.com/developers/applications
- Enable **Privileged Gateway Intents** (at minimum Message Content; Guild Members if you use member sync).
- Invite the bot with appropriate permissions (Manage Roles, Manage Messages, Kick, Ban, etc.).

## Running locally (for testing)
```bash
export DISCORD_TOKEN=...
export DATABASE_URL=postgres://...
export REDIS_URL=redis://...
export PROCESS=bot
python entrypoint.py
```

## Single-service mode
Set `PROCESS=all` to run both the bot and workers inside one Railway service (cheaper, simpler).

## Known issues you will likely hit
- `disco-py` may fail to install or run correctly on Python 3.11 / modern Discord API.
- Some plugins depend on old packages that no longer build.
- The web dashboard OAuth flow needs the Discord redirect URI updated to your Railway domain.
- Table creation on first boot can take a moment; restart once if you see connection errors during initial schema setup.

This package gets the Railway-specific pieces in place. Further Discord API compatibility work is left to you (or a more modern rewrite).
