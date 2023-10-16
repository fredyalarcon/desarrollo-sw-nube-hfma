from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy import func
from flask import jsonify, request
import datetime

from modelos import Task, TaskSchema

task_schema = TaskSchema()

class VistaGenerarToken(Resource):
    def get(self):
        # Crea un token con información de usuario y tiempo de expiración
        expires = datetime.timedelta(minutes=30)
        access_token = create_access_token(identity='frase-secreta', expires_delta=expires)
        
        return jsonify(access_token=access_token)

class VistaTasks(Resource):
    @jwt_required()
    def get(self):
        max = request.args.get('max', default=0)
        order = request.args.get('order', default=0)
        order = int(order)
        #ordenar ascendente
        if order == 0:
            if max == 0:
                tasks = Task.query.order_by(Task.id)
            else:
                max = int(max)
                tasks = Task.query.order_by(Task.id).limit(max)
        else:
            #ordenar descendente
            if order ==1:
                if max == 0:
                    tasks = Task.query.order_by(Task.id.desc())
                else:
                    max = int(max)
                    tasks = Task.query.order_by(Task.id.desc()).limit(max)
                    
        return [task_schema.dump(task) for task in tasks]

class VistaTask(Resource):
    @jwt_required()
    def get(self, id_task):
        return task_schema.dump(Task.query.get_or_404(id_task))
    
class VistaTaskUser(Resource):
    @jwt_required()
    def get(self, usuario_id):
        tasks = Task.query.filter_by(usuario_id=str(usuario_id)).order_by(func.lower(Task.created_at).asc()).all()
        return [task_schema.dump(task) for task in tasks]