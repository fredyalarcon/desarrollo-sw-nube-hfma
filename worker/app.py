from worker import create_app
from flask_restful import Api
import json
import pika 
from converter import Converter
from datetime import datetime
import os
import time

from .modelos import db, Task

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)

rabbit_host = os.environ.get("RABBIT_HOST") or 'localhost'

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
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

def convertFile(file_name, format):
    """
    Supported formats are: ogg, avi, mkv, webm, flv, mov, mp4, mpg
    """
    conv = Converter()


    input_name_file = '{}/{}'.format(UPLOAD_FOLDER, file_name)
    output_name_file = '{}/{}{}.{}'.format(DOWNLOAD_FOLDER, file_name.split('.')[0], datetime.now().timestamp(), format) 
   
    convert = conv.convert(input_name_file, output_name_file, {
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

    return output_name_file

def callback(ch, method, properties, body):
    # Process message:
    payload = json.loads(body)
    id_task = payload['id_task']
    print(' [x] Processing {}, '.format(id_task))

    time.sleep(1)
    task = Task.query.get_or_404(id_task)

    if task.state == 'uploaded':
        # try:
        task.output_name_file = convertFile(task.input_name_file, task.format_output_name_file.lower())
        task.processed_at = datetime.now()
        # except:
        #     print(" [x] An exception occurred")

        task.state = 'processed'
        db.session.commit()
        print(' [x] processed {}, '.format(id_task))

    print(' [x] Done')
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(on_message_callback=callback, queue=queue_name)
print(' [x] Waiting for notify messages.')
channel.start_consuming()
