from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy import func
from flask import jsonify, request
from datetime import datetime, timedelta
import pika 
import json
import os


from api.modelos import db, Task, TaskSchema

task_schema = TaskSchema()

class VistaGenerarToken(Resource):
    def get(self):
        # Crea un token con información de usuario y tiempo de expiración
        expires = timedelta(minutes=30)
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
    
    @jwt_required()
    def post(self):

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(
            exchange='task',
            exchange_type='topic'
        )
        #files
        file = request.files['fileName']
        file_name = file.filename
        # Guarda el archivo en una carpeta, la ruta depende de la variable de entorno
        file.save(os.path.join( os.getenv('UPLOAD_FOLDER'), file_name ))
        #Ruta completa
        input_name_file = f"{str(os.getenv('UPLOAD_FOLDER'))}{file_name}"

        
        new_format = request.form["newFormat"]
        valid_format = ('ogg', 'avi', 'mkv', 'webm', 'flv', 'mov', 'mp4', 'mpg')
        if not valid_format.__contains__(new_format):
            return "El convertidor solo puede convertir a 'ogg', 'avi', 'mkv', 'webm', 'flv', 'mov', 'mp4', 'mpg', revisa el param newFormat"
        task = Task( 
                          state='uploaded', 
                          input_name_file=input_name_file, 
                          output_name_file='', 
                          format_output_name_file=new_format,
                          created_at=datetime.now(),
                          usuario_id=1
                          )
        db.session.add(task)
        db.session.commit()

        # send event
        message = {
            'id_task': task.id
        }
        channel.basic_publish(
            exchange='task',
            routing_key='task.process',
            body=json.dumps(message)
        )
        print(' [x] Sent notify message')
        connection.close()

        return f'Se ha lanzado una nueva tarea de conversion, revisa el status de tu tarea:{task.id}'

class VistaTask(Resource):
    @jwt_required()
    def get(self, id_task):
        return task_schema.dump(Task.query.get_or_404(id_task))
    
    @jwt_required()
    def delete(self, id_task):
        task = Task.query.get_or_404(id_task)
        db.session.delete(task)
        db.session.commit()
        return '',204
    
class VistaTaskUser(Resource):
    @jwt_required()
    def get(self, usuario_id):
        tasks = Task.query.filter_by(usuario_id=str(usuario_id)).order_by(func.lower(Task.created_at).asc()).all()
        return [task_schema.dump(task) for task in tasks]