from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_restful import Resource
from sqlalchemy import func
from flask import jsonify, request, send_from_directory
from datetime import datetime, timedelta
import pika 
import json
import os

from api.modelos import db, Task, TaskSchema

task_schema = TaskSchema()

rabbit_host = os.environ.get("RABBIT_HOST") or 'localhost'

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER') or "../converter_data/in"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')  or "../converter_data/out"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

class VistaDescarga(Resource):
    @jwt_required()
    def get(self, id_task):
        task = Task.query.get_or_404(id_task)
        return send_from_directory(DOWNLOAD_FOLDER, task.output_name_file, as_attachment=True)

class VistaTasks(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        max = request.args.get('max', default=0)
        order = request.args.get('order', default=0)
        order = int(order)
        #ordenar ascendente
        if order == 0:
            if max == 0:
                tasks = Task.query.filter_by(usuario_id=str(current_user_id)).order_by(Task.id)
                #tasks = Task.query.order_by(Task.id)
            else:
                max = int(max)
                #tasks = Task.query.order_by(Task.id).limit(max)
                tasks = Task.query.filter_by(usuario_id=str(current_user_id)).order_by(Task.id).limit(max)
        else:
            #ordenar descendente
            if order ==1:
                if max == 0:
                    tasks = Task.query.filter_by(usuario_id=str(current_user_id)).order_by(Task.id.desc())
                    #tasks = Task.query.order_by(Task.id.desc())
                else:
                    max = int(max)
                    tasks = Task.query.filter_by(usuario_id=str(current_user_id)).order_by(Task.id.desc()).limit(max)
                    #tasks = Task.query.order_by(Task.id.desc()).limit(max)
                    
        return [task_schema.dump(task) for task in tasks]
    
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
        channel = connection.channel()
        channel.exchange_declare(
            exchange='task',
            exchange_type='topic'
        )
        #files
        file = request.files['fileName']
        file_name = file.filename
        # Guarda el archivo en una carpeta, la ruta depende de la variable de entorno
        file.save(os.path.join(UPLOAD_FOLDER, file_name ))
        
        new_format = request.form["newFormat"]
        valid_format = ('ogg', 'avi', 'mkv', 'webm', 'flv', 'mov', 'mp4', 'mpg')
        if not valid_format.__contains__(new_format):
            return "El convertidor solo puede convertir a 'ogg', 'avi', 'mkv', 'webm', 'flv', 'mov', 'mp4', 'mpg', revisa el param newFormat"
        task = Task( 
                          state='uploaded', 
                          input_name_file=file_name, 
                          output_name_file='', 
                          format_output_name_file=new_format,
                          created_at=datetime.now(),
                          usuario_id=current_user_id
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
        try:
            if(task.state == 'uploaded'):
                archivoUpload = os.path.join(UPLOAD_FOLDER, task.input_name_file)
                os.remove(archivoUpload)
            else:
                archivoUpload = os.path.join(UPLOAD_FOLDER, task.input_name_file)
                os.remove(archivoUpload)
                archivoDownload = os.path.join(DOWNLOAD_FOLDER, task.output_name_file)
                os.remove(archivoDownload)
        except OSError:
            return 'Error al eliminar archivo',405
        db.session.delete(task)
        db.session.commit()
        return f'Se ha eliminardo correctamente la tarea: {id_task}'
    
class VistaTaskUser(Resource):
    @jwt_required()
    def get(self, usuario_id):
        tasks = Task.query.filter_by(usuario_id=str(usuario_id)).order_by(func.lower(Task.created_at).asc()).all()
        return [task_schema.dump(task) for task in tasks]