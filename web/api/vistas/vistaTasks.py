from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from sqlalchemy import func
from flask import request, send_from_directory
from datetime import datetime
from google.cloud import storage
from google.cloud import pubsub_v1
import json
import os

from api.modelos import db, Task, TaskSchema

task_schema = TaskSchema()

project_id = os.environ.get("PROJECT_ID") or 'api-converter-403621'
topic_id = os.environ.get("TOPIC_ID") or 'MyTopic'
bucket_name = os.environ.get("BUCKET_NAME") or 'bucket-web-api-converter'
# Usamos barras diagonales dobles o barras diagonales normales para definir la ruta del archivo JSON
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "./static/api-converter-403621-891683842aca.json"

STATIC_FOLDER = './static'

def upload_blob(bucket_name, file, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob('videos/in/{}'.format(destination_blob_name))

    blob.upload_from_string(file.read(), content_type=file.content_type)
   
    print(f"File {file.filename} uploaded to {destination_blob_name}.")

def delete_blob(bucket_name, blob_name):
    """Delete a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    blob.delete()
    print(f"File {blob_name} deleted.")

def download_blob(bucket_name, blob_name, destination_file_name) :
    """Download a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    blob.download_to_filename('videos/out/{}'.format(destination_file_name))
    print(f"File {blob_name} downloaded.")

def publish_message(data_str) -> None:
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    data = data_str.encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data)
    print(future.result())

    print(f"Published messages to {topic_path}.")

class VistaTasks(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        max = request.args.get("max", default=0)
        order = request.args.get("order", default=0)
        order = int(order)
        # ordenar ascendente
        if order == 0:
            if max == 0:
                tasks = Task.query.filter_by(usuario_id=str(current_user_id)).order_by(
                    Task.id
                )
            else:
                max = int(max)
                tasks = (
                    Task.query.filter_by(usuario_id=str(current_user_id))
                    .order_by(Task.id)
                    .limit(max)
                )
        else:
            # ordenar descendente
            if order == 1:
                if max == 0:
                    tasks = Task.query.filter_by(
                        usuario_id=str(current_user_id)
                    ).order_by(Task.id.desc())
                else:
                    max = int(max)
                    tasks = (
                        Task.query.filter_by(usuario_id=str(current_user_id))
                        .order_by(Task.id.desc())
                        .limit(max)
                    )

        return [task_schema.dump(task) for task in tasks]

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        file = request.files["fileName"]
        file_name = "{}-{}".format(int(round(datetime.now().timestamp())), file.filename)
        upload_blob(
            bucket_name,
            file,
            file_name,
        )

        new_format = request.form["newFormat"]
        valid_format = ("ogg", "avi", "mkv", "webm", "flv", "mov", "mp4", "mpg")
        if not valid_format.__contains__(new_format):
            return "El convertidor solo puede convertir a 'ogg', 'avi', 'mkv', 'webm', 'flv', 'mov', 'mp4', 'mpg', revisa el param newFormat"
        task = Task(
            state="uploaded",
            input_name_file=file_name,
            output_name_file="",
            format_output_name_file=new_format,
            created_at=datetime.now(),
            usuario_id=current_user_id,
        )
        db.session.add(task)
        db.session.commit()

        # send event
        message = {"id_task": task.id}
        publish_message(json.dumps(message))
        print(" [x] Sent notify message")

        return f"Se ha lanzado una nueva tarea de conversion, revisa el status de tu tarea:{task.id}"


class VistaTask(Resource):
    @jwt_required()
    def get(self, id_task):
        return task_schema.dump(Task.query.get_or_404(id_task))

    @jwt_required()
    def delete(self, id_task):
        task = Task.query.get_or_404(id_task)
        try:
            delete_blob(bucket_name, 'videos/in/{}'.format(task.input_name_file))
            if task.state == "processed":
                delete_blob(bucket_name, 'videos/out/{}'.format(task.output_name_file))

        except OSError:
            return "Error al eliminar archivo", 405
        db.session.delete(task)
        db.session.commit()
        return f"Se ha eliminado correctamente la tarea: {id_task}"


class VistaTaskUser(Resource):
    @jwt_required()
    def get(self, usuario_id):
        tasks = (
            Task.query.filter_by(usuario_id=str(usuario_id))
            .order_by(func.lower(Task.created_at).asc())
            .all()
        )
        return [task_schema.dump(task) for task in tasks]


class VistaDescarga(Resource):
    def get(self, id_task):
        task = Task.query.get_or_404(id_task)
        download_blob(bucket_name, task.output_name_file, STATIC_FOLDER)
        print(" [x] Downloading file {}".format(task.output_name_file))
        return send_from_directory(
            STATIC_FOLDER, task.output_name_file, as_attachment=True
        )


class VistaHealthCheck(Resource):
    def get(self):
        return "Flask is healthy", 200
