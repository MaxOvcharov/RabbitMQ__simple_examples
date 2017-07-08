# -*- coding: utf-8 -*-
import json
import pika
import time

from optparse import OptionParser


def parse_args_for_migrate_db():
    """
    Configurations of arg-parser for init worker
    :return: options - a dict with input args
    """
    parser = OptionParser()
    parser.add_option('-d', '--delay', dest='callback_delay',
                      help='ADDING DELAY INTO CALLBACK FUNCTION',
                      action='store_true', default=None)
    parser.add_option('-w', '--worker', dest='worker_number',
                      help='MIGRATE TABLES',
                      action='store_true', default=1)
    (options, args) = parser.parse_args()

    return options

options = parse_args_for_migrate_db()
callback_delay = options.callback_delay
worker_number = options.worker_number

conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = conn.channel()
channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    client_message = json.loads(body)
    print(' [x] Received: %s, message_type: %s' % (client_message,
                                                   type(client_message)))
    if callback_delay:
        time.sleep(callback_delay)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='task_queue')
channel.start_consuming()
