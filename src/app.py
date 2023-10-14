from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token
import jwt
import datetime
from modelos import db

from vistas import \
    VistaTasks, VistaTask, \
    VistaTaskUser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql@localhost/converter'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['JWT_SECRET_KEY'] = 'frase-secreta'
#app.config['JWT_ALGORITHM'] = 'HS256'
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()

@app.route('/generar_token')
def generar_token():
    # Crea un token con información de usuario y tiempo de expiración
    expires = datetime.timedelta(minutes=30)
    access_token = create_access_token(identity='frase-secreta', expires_delta=expires)
    
    return jsonify(access_token=access_token)

db.init_app(app)
ma = Marshmallow(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(VistaTasks, '/tasks')
api.add_resource(VistaTask, '/tasks/<int:id_task>')
api.add_resource(VistaTaskUser, '/tasks/usuario/<int:usuario_id>')
jwt = JWTManager(app)