import base64
from worker import create_app
from flask_restful import Api
from flask_restful import Resource
from google.cloud import storage
from concurrent.futures import TimeoutError
from concurrent import futures
from google.cloud import pubsub_v1
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask import request
import json
import os
import time
import ffmpeg


from .modelos import db, Task

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)

STATIC_FOLDER = './static'

os.makedirs('{}/videos/in'.format(STATIC_FOLDER), exist_ok=True)
os.makedirs('{}/videos/out'.format(STATIC_FOLDER), exist_ok=True)

bucket_name = os.environ.get("BUCKET_NAME") or 'bucket-web-converter'

# Usamos barras diagonales dobles o barras diagonales normales para definir la ruta del archivo JSON
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "./static/flowing-lead-403123-4aa6b888e3a2.json"

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob('videos/out/{}'.format(destination_blob_name))

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )


def download_blob(bucket_name, blob_name, destination_file_name) :
    """Download a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob('videos/in/{}'.format(blob_name))
    blob.download_to_filename(destination_file_name)
    print(f"File {blob_name} downloaded.")

def convertFile(id_task, file_name, format):
    """
    Supported formats are: ogg, avi, mkv, webm, flv, mov, mp4, mpg
    """

    input_path_file = '{}/videos/in/{}'.format(STATIC_FOLDER, file_name)

    if (not os.path.isfile(input_path_file)):
        download_blob(bucket_name, file_name, input_path_file)

    output_file_name = '{}-{}.{}'.format(id_task, file_name.split('.')[0], format)
    output_path_file = '{}/videos/out/{}'.format(STATIC_FOLDER, output_file_name) 
   
    if (not os.path.isfile(output_path_file)):
        (
            ffmpeg
            .input(input_path_file)
            .filter('fps', fps=15)
            .output(output_path_file, vcodec='h264', threads=1, crf=28, preset='medium', movflags='faststart', pix_fmt='yuv420p')
            .run()
        )

    upload_blob(
        bucket_name,
        output_path_file,
        output_file_name,
    )

    os.remove(input_path_file)
    os.remove(output_path_file)

    return output_file_name


class VistaHealthCheck(Resource):
    def get(self):
        return "Flask is healthy", 200
    

class VistaWorkerTask(Resource):
    def post(self):

        decodedBytes = base64.b64decode(request.form["message"].data)
        decodedStr = decodedBytes.decode("utf-8") 
        data = json.loads(decodedStr)
        id_task = data.id_task

        # Process message:
        print(' [x] Processing {}, '.format(id_task))

        task = Task.query.get_or_404(id_task)

        if task.state == 'uploaded':
            try:
                task.output_name_file = convertFile(id_task, task.input_name_file, task.format_output_name_file.lower())
                task.processed_at = datetime.now()
            except:
                print(" [x] An exception occurred during video convertion")

            task.state = 'processed'
            db.session.commit()
            print(' [x] processed {}, '.format(id_task))
            
        return "Ok", 200

api.add_resource(VistaHealthCheck, '/health-check')
api.add_resource(VistaWorkerTask, '/worker-task')