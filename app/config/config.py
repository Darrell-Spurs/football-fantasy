import datetime, os
from os.path import dirname
class BaseConfig:
    SEND_FILE_MAX_AGE_DEFAULT = 0
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)
    SECRET_KEY = os.urandom(12)
    PORT = 5000
    TASK_ROUTES = ([
        ('celtest.add', {'queue': 'celery'}),
        ('celtest.mul', {'queue': 'celery2'}),
    ],)
    FCBOGNDFKIYG = "golden_key.json"
    EXPLAIN_TEMPLATE_LOADING = True

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SELENIUM = "LOCAL_FILE"
    # PREFERRED_URL_SCHEME = "http"
    HOST = "127.0.0.1"
    TEMPLATE_FOLDER = os.getcwd()+r"\static\templates"
    STATIC_FOLDER = os.getcwd()+r"\static"
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
    CELERY_TASK_SERIALIZER = 'json'

class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SELENIUM = "BINARY"
    # PREFERRED_URL_SCHEME = "https"
    HOST = "0.0.0.0"
    TEMPLATE_FOLDER = r"/app/static/templates"
    STATIC_FOLDER = r"/app/static"
    CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL")
    CELERY_BROKER_URL = os.environ.get("REDIS_URL")

configuration = {
    "development": DevelopmentConfig,
    "testing": TestingConfig
}