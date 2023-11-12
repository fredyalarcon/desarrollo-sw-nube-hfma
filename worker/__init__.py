from flask import Flask
import os

db_host = os.environ.get("DB_HOST") or '10.128.0.7'

def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mysql2:mysql@{}:3306/converter'.format(db_host)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    return app