from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from modelos import db
from vistas import \
    VistaTasks

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgresql@localhost:5432/converter'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()

db = SQLAlchemy(app)
migrate = Migrate(app, db)
#db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(VistaTasks, '/tasks')

jwt = JWTManager(app)