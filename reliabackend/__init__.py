import sys
from flask import Flask
from flask_redis import FlaskRedis
from werkzeug.middleware.proxy_fix import ProxyFix

from weblablib import WebLab

from config import configurations

# Plugins
redis_store = FlaskRedis()
weblab = WebLab()


def create_app(config_name: str = 'default'):
    # Based on Flasky https://github.com/miguelgrinberg/flasky
    app = Flask(__name__)
    app.config.from_object(configurations[config_name])

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    # Initialize plugins
    redis_store.init_app(app)
    weblab.init_app(app)

    # Register views
    from .views.main import main_blueprint
    from .views.data import data_blueprint
    from .views.user import user_blueprint
    from .views.files import files_blueprint

    @app.route('/api/')
    def api_index():
        return "Welcome to the API"

    app.register_blueprint(main_blueprint)
    app.register_blueprint(data_blueprint, url_prefix='/api/data')
    app.register_blueprint(user_blueprint, url_prefix='/api/user')
    app.register_blueprint(files_blueprint, url_prefix='/api/user/files')

    return app
