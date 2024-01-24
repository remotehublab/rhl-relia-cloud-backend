import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    REDIS_URL = os.environ.get('REDIS_URL') or "redis://localhost/0"
    WEBLAB_USERNAME = os.environ.get('WEBLAB_USERNAME')
    WEBLAB_PASSWORD = os.environ.get('WEBLAB_PASSWORD')
    WEBLAB_TIMEOUT = int(os.environ.get('WEBLAB_TIMEOUT') or '7200')
    WEBLAB_CALLBACK_URL = '/weblab/relia-callback'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    USE_FAKE_USERS = False
    CDN_URL = os.environ.get('CDN_URL')
    SCHEDULER_BASE_URL = os.environ.get('SCHEDULER_BASE_URL')
    SCHEDULER_TOKEN = os.environ.get('SCHEDULER_TOKEN')
    REDIRECT_URL = os.environ.get('REDIRECT_URL')
    USE_FIREJAIL = os.environ.get('USE_FIREJAIL', '0') in ('1', 'true', 'True')
    FIREJAIL_IP_ADDRESS = os.environ.get('FIREJAIL_IP_ADDRESS') or '10.10.20.2'
    FIREJAIL_INTERFACE = os.environ.get('FIREJAIL_INTERFACE') or 'br0'

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'secret'
    WEBLAB_USERNAME = os.environ.get('WEBLAB_USERNAME') or 'weblab'
    WEBLAB_PASSWORD = os.environ.get('WEBLAB_PASSWORD') or 'password'
    USE_FAKE_USERS = os.environ.get('USE_FAKE_USERS', '1') in ('1', 'true', 'True')
    CDN_URL = os.environ.get('CDN_URL') or 'http://localhost:3000/'
    SCHEDULER_BASE_URL = os.environ.get('SCHEDULER_BASE_URL') or 'http://localhost:6002'
    SCHEDULER_TOKEN = os.environ.get('SCHEDULER_TOKEN') or 'password'
    REDIRECT_URL = os.environ.get('REDIRECT_URL') or 'https://rhlab.ece.uw.edu/projects/relia/'

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
