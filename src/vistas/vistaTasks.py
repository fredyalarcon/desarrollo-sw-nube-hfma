from flask_jwt_extended import jwt_required
from flask_restful import Resource

from modelos import Task, TaskSchema

task_schema = TaskSchema()

class VistaTasks(Resource):
    #@jwt_required()
    def get(self):
        tasks = Task.query.all()
        return [task_schema.dump(task) for task in tasks]