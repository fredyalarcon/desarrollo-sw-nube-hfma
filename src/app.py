from flask import Flask
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager
from modelos import db

from vistas import \
    VistaTasks, VistaTask, \
    VistaTaskUser, VistaGenerarToken

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql@localhost/converter'
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
api.add_resource(VistaGenerarToken, '/generar_token')
api.add_resource(VistaTasks, '/tasks')
api.add_resource(VistaTask, '/task/<int:id_task>')
api.add_resource(VistaTaskUser, '/tasks/usuario/<int:usuario_id>')
jwt = JWTManager(app)