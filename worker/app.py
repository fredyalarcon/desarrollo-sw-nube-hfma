from worker import create_app
from flask_restful import Api
import json
import pika 

from .modelos import db, Task

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
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

def callback(ch, method, properties, body):
    # Process message:
    payload = json.loads(body)
    id_task = payload['id_task']
    print(' [x] Processing {}, '.format(id_task))

    task = Task.query.get_or_404(id_task)

    if task.state == 'uploaded':
        task.state = 'processed'
        db.session.commit()
        print(' [x] processed {}, '.format(id_task))

    print(' [x] Done')
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(on_message_callback=callback, queue=queue_name)
print(' [x] Waiting for notify messages.')
channel.start_consuming()
