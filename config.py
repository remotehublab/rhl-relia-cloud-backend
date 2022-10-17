import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    REDIS_URL = os.environ.get('REDIS_URL') or "redis://localhost/0"
    WEBLAB_USERNAME = os.environ.get('WEBLAB_USERNAME')
    WEBLAB_PASSWORD = os.environ.get('WEBLAB_PASSWORD')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    USE_FAKE_USERS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'secret'
    WEBLAB_USERNAME = os.environ.get('WEBLAB_USERNAME') or 'weblab'
    WEBLAB_PASSWORD = os.environ.get('WEBLAB_PASSWORD') or 'password'
    USE_FAKE_USERS = os.environ.get('USE_FAKE_USERS', '1') in ('1', 'true', 'True')

class StagingConfig(Config):
    DEBUG = False

class ProductionConfig(Config):
    DEBUG = False

configurations = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
