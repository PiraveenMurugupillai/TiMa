import os

basedir = os.path.abspath(os.path.dirname(__file__))

secret_key_file = os.environ.get('SECRET_KEY_FILE')
secret_key = None
if secret_key_file:
    secret_key = open(secret_key_file).read()


class Config(object):
    SECRET_KEY = secret_key or 'ein-geheim-code-den-niemand-kennt'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
