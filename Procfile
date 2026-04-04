# Safe default remains gthread, but worker model/tuning is env-configurable via gunicorn_conf.py.
web: gunicorn -c gunicorn_conf.py wsgi:app
worker: rq worker --url $REDIS_URL ai_replies
