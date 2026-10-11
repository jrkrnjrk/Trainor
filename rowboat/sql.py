import os
try:
    import psycogreen.gevent
    psycogreen.gevent.patch_psycopg()
except ImportError:
    pass

from peewee import Proxy, OP, Model
from peewee import Expression
from playhouse.postgres_ext import PostgresqlExtDatabase
from urllib.parse import urlparse

REGISTERED_MODELS = []

database = Proxy()

OP['IRGX'] = 'irgx'


def pg_regex_i(lhs, rhs):
    return Expression(lhs, OP.IRGX, rhs)


try:
    if hasattr(PostgresqlExtDatabase, 'register_ops'):
        PostgresqlExtDatabase.register_ops({OP.IRGX: '~*'})
except Exception:
    pass


class BaseModel(Model):
    class Meta:
        database = database

    @staticmethod
    def register(cls):
        REGISTERED_MODELS.append(cls)
        return cls


def init_db(env):
    database_url = os.getenv('DATABASE_URL') or os.getenv('DSN') or os.getenv('POSTGRES_URL')

    if database_url:
        if database_url.startswith('postgres://'):
            database_url = 'postgresql://' + database_url[len('postgres://'):]
        parsed = urlparse(database_url)
        dbname = parsed.path.lstrip('/') or os.getenv('PGDATABASE', 'railway')
        print(f"[sql] Connecting via DATABASE_URL to {parsed.hostname}:{parsed.port or 5432}/{dbname}")
        database.initialize(PostgresqlExtDatabase(
            dbname,
            user=parsed.username or os.getenv('PGUSER'),
            password=parsed.password or os.getenv('PGPASSWORD'),
            host=parsed.hostname or os.getenv('PGHOST'),
            port=parsed.port or int(os.getenv('PGPORT', 5432)),
            autorollback=True,
        ))
    elif os.getenv('PGHOST'):
        # Railway also exposes individual PG* vars
        print(f"[sql] Connecting via PGHOST={os.getenv('PGHOST')}")
        database.initialize(PostgresqlExtDatabase(
            os.getenv('PGDATABASE', 'railway'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            host=os.getenv('PGHOST'),
            port=int(os.getenv('PGPORT', 5432)),
            autorollback=True,
        ))
    else:
        print("[sql] WARNING: No DATABASE_URL or PGHOST set. Falling back to local socket (this will fail on Railway).")
        print("[sql] Set DATABASE_URL by referencing your Postgres service in Railway Variables.")
        database.initialize(PostgresqlExtDatabase(
            'rowboat',
            user='rowboat',
            port=int(os.getenv('PG_PORT', 5432)),
            autorollback=True))

    for model in REGISTERED_MODELS:
        try:
            model.create_table(True)
            if hasattr(model, 'SQL'):
                database.execute_sql(model.SQL)
        except Exception as e:
            print(f"[sql] Warning creating table for {model}: {e}")


def reset_db():
    init_db(os.getenv('ENV', 'local'))

    for model in REGISTERED_MODELS:
        model.drop_table(True)
        model.create_table(True)
