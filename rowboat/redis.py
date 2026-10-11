from __future__ import absolute_import

import os
import json

import redis
from urllib.parse import urlparse

ENV = os.getenv('ENV', 'local')

redis_url = os.getenv('REDIS_URL')
if redis_url:
    parsed = urlparse(redis_url)
    rdb = redis.Redis(
        host=parsed.hostname or 'localhost',
        port=parsed.port or 6379,
        password=parsed.password,
        db=int(parsed.path.lstrip('/') or 0),
        decode_responses=False,
    )
elif ENV == 'docker':
    rdb = redis.Redis(db=0, host='redis')
else:
    rdb = redis.Redis(db=11)


def emit(typ, **kwargs):
    kwargs['type'] = typ
    rdb.publish('actions', json.dumps(kwargs))
