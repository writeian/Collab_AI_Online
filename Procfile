# gthread: extra threads help concurrent SSE without spawning many processes (watch RAM on small hosts).
web: gunicorn wsgi:app --bind 0.0.0.0:$PORT -k gthread --workers 3 --threads 12 --timeout 300
worker: rq worker --url $REDIS_URL ai_replies
