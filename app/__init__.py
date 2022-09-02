"""
Initialization of app module
"""

from config import Config
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import os

# initialize Flask app with configs, database & logging
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login_page'

# create folder for logs, if it does not exist already
if not os.path.exists('logs'):
    os.mkdir('logs')

# configuration for logging
file_handler = RotatingFileHandler('logs/tima.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# first log on every startup of the application
app.logger.info('TiMa startup')


from app import routes, models, errors, api
