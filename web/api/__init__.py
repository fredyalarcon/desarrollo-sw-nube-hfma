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
db_user = os.environ.get("DB_USER") or 'root'
db_password = os.environ.get("DB_PASSWORD") or 'mysql'
db_name = os.environ.get("DB_NAME") or 'converter'

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}:3306/{}'.format(db_user, db_password, db_host, db_name)
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