web: python main.py
beat: celery -A celtest beat --loglevel=INFO -E
worker: celery -A celtest worker --loglevel=INFO -P solo -E
