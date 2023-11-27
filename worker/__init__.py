from flask import Flask
import os

db_host = os.environ.get("DB_HOST") or 'localhost'
db_user = os.environ.get("DB_USER") or 'root'
db_password = os.environ.get("DB_PASSWORD") or 'mysql'
db_name = os.environ.get("DB_NAME") or 'converter'
project_id ="flowing-lead-403123"
INSTANCE_NAME ="flowing-lead-403123:us-central1:cloud-sql-mysql"
db_ip = os.environ.get("DB_HOST") or '35.239.3.249'

def create_app(config_name):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]= 'mysql+pymysql://{user}:{password}@{ip}/{database}'.format(
        user=db_user, password=db_password,
        ip=db_ip, database=db_name,
        project=project_id, instance_name=INSTANCE_NAME)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}:3306/{}'.format(db_user, db_password, db_host, db_name)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = True
    return app