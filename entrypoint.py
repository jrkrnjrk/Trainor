#!/usr/bin/env python3
"""
Railway entrypoint for Rowboat.
Generates config.yaml from environment variables, then starts the selected process.

Environment variables:
  DISCORD_TOKEN     (required)  Bot token
  DATABASE_URL      (auto)      Injected by Railway Postgres
  REDIS_URL         (auto)      Injected by Railway Redis
  SECRET_KEY        (optional)  Flask secret
  PROCESS           (optional)  bot | workers | web | all   (default: bot)
  PORT              (optional)  Railway injects this for the web service
"""
import os
import sys
import subprocess
import time

import yaml


def generate_config():
    token = os.environ.get("DISCORD_TOKEN") or os.environ.get("TOKEN")
    if not token:
        print("ERROR: DISCORD_TOKEN (or TOKEN) must be set", file=sys.stderr)
        sys.exit(1)

    config = {
        "token": token,
        "DSN": os.environ.get("DATABASE_URL", ""),
        "manhole_enable": False,
        "manhole_bind": "127.0.0.1:7171",
        "state": {
            "sync_guild_members": os.environ.get("SYNC_GUILD_MEMBERS", "false").lower() == "true",
        },
        "bot": {
            "commands_enabled": True,
            "plugins": [
                "rowboat.plugins.core",
                "rowboat.plugins.modlog",
                "rowboat.plugins.admin",
                "rowboat.plugins.infractions",
                "rowboat.plugins.spam",
                "rowboat.plugins.censor",
                "rowboat.plugins.utilities",
                "rowboat.plugins.sql",
                "rowboat.plugins.internal",
                "rowboat.plugins.stats",
            ],
        },
        "web": {
            "SECRET_KEY": os.environ.get("SECRET_KEY", "rowboat-railway-secret-change-me"),
            "DISCORD_CLIENT_ID": os.environ.get("DISCORD_CLIENT_ID", ""),
            "DISCORD_CLIENT_SECRET": os.environ.get("DISCORD_CLIENT_SECRET", ""),
            "DISCORD_REDIRECT_URI": os.environ.get("DISCORD_REDIRECT_URI", ""),
            "DISCORD_AUTH_URL": "https://discord.com/api/oauth2/authorize",
            "DISCORD_TOKEN_URL": "https://discord.com/api/oauth2/token",
            "DISCORD_API_BASE_URL": "https://discord.com/api",
        },
    }

    with open("config.yaml", "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False)
    print("Wrote config.yaml from environment variables")


def run_process(process):
    env = os.environ.copy()
    env["ENV"] = env.get("ENV", "railway")

    if process == "bot":
        cmd = ["python", "manage.py", "bot", "-e", "railway"]
    elif process == "workers":
        cmd = ["python", "manage.py", "workers"]
    elif process == "web":
        # Railway expects the web process to listen on $PORT
        # Use gevent.pywsgi (gevent.wsgi was removed in modern gevent)
        port = os.environ.get("PORT", "8686")
        cmd = [
            "python", "-c",
            f"from gevent.pywsgi import WSGIServer; from rowboat.web import rowboat; "
            f"WSGIServer(('0.0.0.0', {port}), rowboat.app).serve_forever()"
        ]
    else:
        print(f"Unknown PROCESS={process}", file=sys.stderr)
        sys.exit(1)

    print(f"Starting process: {process} -> {' '.join(cmd)}")
    os.execvpe(cmd[0], cmd, env)


def run_all():
    """Run workers + bot in background, web in foreground (single Railway service)."""
    env = os.environ.copy()
    env["ENV"] = env.get("ENV", "railway")

    print("Starting workers in background...")
    workers = subprocess.Popen(
        ["python", "manage.py", "workers"],
        env=env,
    )

    print("Starting bot in background...")
    bot = subprocess.Popen(
        ["python", "manage.py", "bot", "-e", "railway"],
        env=env,
    )

    time.sleep(2)

    # Web in foreground so Railway sees a listening port
    port = os.environ.get("PORT", "8080")
    print(f"Starting web on port {port}...")
    try:
        web = subprocess.Popen(
            ["python", "-c",
             f"from gevent.pywsgi import WSGIServer; from rowboat.web import rowboat; "
             f"WSGIServer(('0.0.0.0', {port}), rowboat.app).serve_forever()"],
            env=env,
        )
        ret = web.wait()
        workers.terminate()
        bot.terminate()
        sys.exit(ret)
    except KeyboardInterrupt:
        workers.terminate()
        bot.terminate()
        sys.exit(0)


if __name__ == "__main__":
    generate_config()
    process = os.environ.get("PROCESS", "bot").lower()

    if process == "all":
        run_all()
    else:
        run_process(process)
