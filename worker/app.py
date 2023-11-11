from worker import create_app
from flask_restful import Api
import json
import pika 
from converter import Converter
from datetime import datetime
import os
import time
from google.cloud import storage

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

bucket_name = "bucket-web-api-converter"

# Usamos barras diagonales dobles o barras diagonales normales para definir la ruta del archivo JSON
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "./static/api-converter-403621-891683842aca.json"


rabbit_host = os.environ.get("RABBIT_HOST") or '10.128.0.4'

credentials = pika.PlainCredentials('rabbit', 'rabbit')
parameters = pika.ConnectionParameters(rabbit_host,
                                   5672,
                                   '/',
                                   credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

queue = channel.queue_declare('task_process')
queue_name = queue.method.queue

channel.exchange_declare(
    exchange='task',
    exchange_type='topic'
)

channel.queue_bind(
    exchange='task',
    queue=queue_name,
    routing_key='task.process' # binding key
)

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

def convertFile(file_name, format):
    """
    Supported formats are: ogg, avi, mkv, webm, flv, mov, mp4, mpg
    """
    conv = Converter()

    input_path_file = '{}/videos/in/{}'.format(STATIC_FOLDER, file_name)
    download_blob(bucket_name, file_name, input_path_file)

    output_file_name = '{}.{}'.format(file_name.split('.')[0], format)
    output_path_file = '{}/videos/out/{}'.format(STATIC_FOLDER, output_file_name) 
   
    convert = conv.convert(input_path_file, output_path_file, {
        'format': format,
        'audio': {
            'codec': 'mp3',
            'samplerate': 11025,
            'channels': 2
        },
        'video': {
            'codec': 'h264',
            'width': 720,
            'height': 400,
            'fps': 15
        }
        })

    for timecode in convert:
        print(f'\rConverting ({timecode:.2f}) ...')

    upload_blob(
        bucket_name,
        output_path_file,
        output_file_name,
    )

    return output_file_name

def callback(ch, method, properties, body):
    # Process message:
    payload = json.loads(body)
    id_task = payload['id_task']
    print(' [x] Processing {}, '.format(id_task))

    time.sleep(1)
    task = Task.query.get_or_404(id_task)

    if task.state == 'uploaded':
        try:
            task.output_name_file = convertFile(task.input_name_file, task.format_output_name_file.lower())
            task.processed_at = datetime.now()
        except:
            print(" [x] An exception occurred")

        task.state = 'processed'
        db.session.commit()
        print(' [x] processed {}, '.format(id_task))

    print(' [x] Done')
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(on_message_callback=callback, queue=queue_name)
print(' [x] Waiting for notify messages.')
channel.start_consuming()
