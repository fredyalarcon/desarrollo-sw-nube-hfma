from flask import Flask
import os

db_host = os.environ.get("DB_HOST") or 'localhost'
db_user = os.environ.get("DB_USER") or 'root'
db_password = os.environ.get("DB_PASSWORD") or 'mysql'
db_name = os.environ.get("DB_NAME") or 'converter'

def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}:3306/{}'.format(db_user, db_password, db_host, db_name)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    return app