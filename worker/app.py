from worker import create_app
from flask_restful import Api
from google.cloud import storage
from concurrent.futures import TimeoutError
from google.api_core import retry
from google.cloud import pubsub_v1
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
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

bucket_name = "bucket-web-api-converter"

# Usamos barras diagonales dobles o barras diagonales normales para definir la ruta del archivo JSON
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "./static/api-converter-403621-891683842aca.json"

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

    input_path_file = '{}/videos/in/{}'.format(STATIC_FOLDER, file_name)

    if (not os.path.isfile(input_path_file)):
        download_blob(bucket_name, file_name, input_path_file)

    output_file_name = '{}.{}'.format(file_name.split('.')[0], format)
    output_path_file = '{}/videos/out/{}'.format(STATIC_FOLDER, output_file_name) 
   
    if (not os.path.isfile(output_path_file)):
        (
            ffmpeg
            .input(input_path_file)
            .filter('fps', fps=15)
            .output(output_path_file, vcodec='h264', crf=28, preset='fast', movflags='faststart', pix_fmt='yuv420p')
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

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    # Process message:
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    session = scoped_session(sessionmaker(bind=engine))
    
    data = json.loads(message.data.decode('utf-8'))
    id_task = data['id_task']
    print(' [x] Processing {}, '.format(id_task))

    time.sleep(1)
    task = session.query(Task).get(id_task)

    if task.state == 'uploaded':
        try:
            task.output_name_file = convertFile(task.input_name_file, task.format_output_name_file.lower())
            task.processed_at = datetime.now()
        except:
            print(" [x] An exception occurred during video convertion")

        task.state = 'processed'
        session.commit()
        print(' [x] processed {}, '.format(id_task))
        session.remove()

    message.ack()
    print(' [x] Done')
    

project_id = "api-converter-403621"
subscription_id = "MySub"
# Number of seconds the subscriber should listen for messages
# timeout = 5.0

# Limit the subscriber to only have ten outstanding messages at a time.
max_messages=1

subscriber = pubsub_v1.SubscriberClient()
# The `subscription_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/subscriptions/{subscription_id}`
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# Wrap the subscriber in a 'with' block to automatically call close() to
# close the underlying gRPC channel when done.
with subscriber:
    # The subscriber pulls a specific number of messages. The actual
    # number of messages pulled may be smaller than max_messages.
    response = subscriber.pull(
        request={"subscription": subscription_path, "max_messages": max_messages},
        retry=retry.Retry(deadline=60),
    )

    if len(response.received_messages) != 0:
        ack_ids = []
        for received_message in response.received_messages:
            print(f"Received: {received_message.message.data}.")
            ack_ids.append(received_message.ack_id)
        try:
            callback(received_message)
        except:
            print(" [x] An exception occurred during processing the task ")