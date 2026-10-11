import os
import logging

try:
    from disco.util.logging import LOG_FORMAT
except Exception:
    LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

try:
    from raven import Client
    from raven.transport.gevent import GeventedHTTPTransport
    HAS_RAVEN = True
except Exception:
    HAS_RAVEN = False

ENV = os.getenv('ENV', 'local')
DSN = os.getenv('DSN') or os.getenv('SENTRY_DSN')

try:
    import subprocess
    REV = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).strip().decode()
except Exception:
    REV = 'railway'

VERSION = '1.3.0-railway'

if HAS_RAVEN and DSN:
    raven_client = Client(
        DSN,
        ignore_exceptions=['KeyboardInterrupt'],
        release=REV,
        environment=ENV,
        transport=GeventedHTTPTransport,
    )
else:
    class _DummyRaven:
        def captureException(self, *a, **k):
            pass
        def captureMessage(self, *a, **k):
            pass
    raven_client = _DummyRaven()

# Log things to file
file_handler = logging.FileHandler('rowboat.log')
log = logging.getLogger()
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
log.addHandler(file_handler)
