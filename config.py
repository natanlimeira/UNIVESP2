import os
basedir = os.path.abspath(os.path.dirname(__file__))
#configuração do login e afins
class Config(object):
    # ...
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'cards.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False