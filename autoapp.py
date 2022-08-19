import os
from reliaweb import create_app
application = create_app(os.environ.get('FLASK_CONFIG') or 'default')
