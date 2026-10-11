import os; os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import logging

from flask import Flask, g, session
from holster.flask_ext import Holster

from rowboat import ENV
from rowboat.sql import init_db
from rowboat.models.user import User
from rowboat.types.guild import PluginsConfig

from yaml import safe_load as load

rowboat = Holster(Flask(__name__))
logging.getLogger('peewee').setLevel(logging.DEBUG)


def _init_app():
    init_db(ENV)

    PluginsConfig.force_load_plugin_configs()

    with open('config.yaml', 'r') as f:
        data = load(f) or {}

    web_cfg = data.get('web', {})
    rowboat.app.config.update(web_cfg)
    rowboat.app.secret_key = web_cfg.get('SECRET_KEY', 'rowboat-railway-secret')
    rowboat.app.config['token'] = data.get('token')


# Run once at startup (before_first_request was removed in Flask 2.3+)
_init_app()


@rowboat.app.before_request
def check_auth():
    g.user = None

    if 'uid' in session:
        g.user = User.with_id(session['uid'])


@rowboat.app.after_request
def save_auth(response):
    if g.user and 'uid' not in session:
        session['uid'] = g.user.id
    elif not g.user and 'uid' in session:
        del session['uid']

    return response


@rowboat.app.context_processor
def inject_data():
    return dict(
        user=g.user,
    )
