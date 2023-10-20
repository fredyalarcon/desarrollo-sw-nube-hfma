from api import create_app
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager
from .modelos import db

from .vistas import \
    VistaTasks, VistaTask, \
    VistaSignup, VistaLogin, \
    VistaTaskUser, VistaDescarga

app = create_app('default_api')
app_context = app.app_context()
app_context.push()

db.init_app(app)
ma = Marshmallow(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(VistaSignup, '/signup')
api.add_resource(VistaLogin, '/login')
api.add_resource(VistaDescarga, '/downloadfile/<int:id_task>')
api.add_resource(VistaTasks, '/tasks')
api.add_resource(VistaTask, '/task/<int:id_task>')
api.add_resource(VistaTaskUser, '/tasks/usuario/<int:usuario_id>')
jwt = JWTManager(app)