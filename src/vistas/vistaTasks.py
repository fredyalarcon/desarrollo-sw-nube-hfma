from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy import func

from modelos import Task, TaskSchema

task_schema = TaskSchema()

class VistaTasks(Resource):
    #@jwt_required()
    def get(self):
        tasks = Task.query.all()
        return [task_schema.dump(task) for task in tasks]

class VistaTask(Resource):
    #@jwt_required()
    def get(self, id_task):
        return task_schema.dump(Task.query.get_or_404(id_task))
    
class VistaTaskUser(Resource):
    #@jwt_required()
    def get(self, usuario_id):
        tasks = Task.query.filter_by(usuario_id=str(usuario_id)).order_by(func.lower(Task.created_at).asc()).all()
        return [task_schema.dump(task) for task in tasks]