web: gunicorn wsgi:app --bind 0.0.0.0:$PORT -k gthread --workers 3 --threads 8 --timeout 300
worker: rq worker --url $REDIS_URL ai_replies
