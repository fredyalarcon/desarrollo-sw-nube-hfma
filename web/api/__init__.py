from flask import Flask
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager
import os

from .modelos import db

from .vistas import \
    VistaTasks, VistaTask, \
    VistaSignup, VistaLogin, \
    VistaTaskUser, VistaDescarga, \
    VistaHealthCheck

db_host = os.environ.get("DB_HOST") or 'localhost'
db_user = os.environ.get("DB_USER") or 'mysql2'
db_password = os.environ.get("DB_PASSWORD") or 'mysql'
db_name = os.environ.get("DB_NAME") or 'converter'
project_id ="flowing-lead-403123"
INSTANCE_NAME ="flowing-lead-403123:us-central1:cloud-sql-mysql"
db_ip = os.environ.get("DB_HOST") or '35.239.3.249'

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]= 'mysql+pymysql://{user}:{password}@{ip}/{database}'.format(
        user=db_user, password=db_password,
        ip=db_ip, database=db_name,
        project=project_id, instance_name=INSTANCE_NAME)
    # Configurar la cadena de conexión en función del entorno
    # if sys.platform != 'win32':  # Verificar si no es un sistema Windows
    #     CONNECTION_NAME = 'flowing-lead-403123:us-central1:cloud-sql-mysql'
    #     SQLALCHEMY_DATABASE_URI = (
    #         'mysql+pymysql://{user}:{password}@localhost/{database}'
    #         '?unix_socket=/cloudsql/{connection_name}').format(
    #             user=db_user, password=db_password,
    #             database=db_name, connection_name=CONNECTION_NAME)
    # else:
    #     SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}:3306/{database}'.format(
    #         user=db_user, password=db_password,
    #         host=db_host, database=db_name)
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}:3306/{}'.format(db_user, db_password, db_host, db_name)
    #app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS'] = True

    app_context = app.app_context()
    app_context.push()

    db.init_app(app)
    ma = Marshmallow(app)
    db.create_all()

    cors = CORS(app)

    api = Api(app)
    api.add_resource(VistaSignup, '/signup')
    api.add_resource(VistaLogin, '/login')
    api.add_resource(VistaTasks, '/tasks')
    api.add_resource(VistaTask, '/task/<int:id_task>')
    api.add_resource(VistaTaskUser, '/tasks/usuario/<int:usuario_id>')
    api.add_resource(VistaDescarga, '/download_file/<int:id_task>')
    api.add_resource(VistaHealthCheck, '/health-check')
    jwt = JWTManager(app)
    return app