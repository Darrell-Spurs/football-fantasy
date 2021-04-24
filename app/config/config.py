import datetime, os


class BaseConfig:
    SEND_FILE_MAX_AGE_DEFAULT = 0
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)
    SECRET_KEY = os.urandom(12)
    PORT = 5000
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
    TASK_ROUTES = ([
        ('celtest.add', {'queue': 'celery'}),
        ('celtest.mul', {'queue': 'celery2'}),
    ],)

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SELENIUM = "LOCAL_FILE"
    # PREFERRED_URL_SCHEME = "http"
    HOST = "127.0.0.1"
    GOLDEN_KEY = os.getcwd() + "\static\golden_key.json"

class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SELENIUM = "BINARY"
    # PREFERRED_URL_SCHEME = "https"
    HOST = "0.0.0.0"
    GOLDEN_KEY = os.environ.get("golden_key")


configuration = {
    "development": DevelopmentConfig,
    "testing": TestingConfig
}