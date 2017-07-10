# -*- coding: utf-8 -*-
import json
import pika
import time

from optparse import OptionParser

SERVER_LIST = ['s_1', 's_2', 's_3']


def parse_args_for_init_worker():
    """
    Configurations of arg-parser for init worker
    :return: options - a dict with input args
    """
    parser = OptionParser()
    parser.add_option('-d', '--delay', dest='callback_delay',
                      help='ADDING DELAY INTO CALLBACK FUNCTION',
                      type='int', default=None)
    parser.add_option('-w', '--worker', dest='worker_number',
                      help='CREATE NUMBER OF WORKERS',
                      type='int', default=1)
    parser.add_option('-k', '--routing_key', dest='routing_key',
                      help='CHOSE ROUTING KEY FROM SERVER_LIST = {}'.format(SERVER_LIST),
                      type='int')
    options, args = parser.parse_args()
    if not options.routing_key:
        parser.error('Routing key is mandatory for running worker. Example: -routing_key 1,'
                     ' choose the first routing_key from SERVER_LIST= {}'.format(SERVER_LIST))

    return options

opt = parse_args_for_init_worker()
callback_delay = opt.callback_delay
worker_number = opt.worker_number
routing_key = SERVER_LIST[opt.routing_key]
task_counter = 1

conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = conn.channel()
channel.exchange_declare(exchange='direct_message', exchange_type='direct')
res = channel.queue_declare(exclusive=True)
queue_name = res.method.queue
channel.queue_bind(exchange='direct_message', queue=queue_name, routing_key=routing_key)
print(' [*] Waiting for messages. Routing key: {0}, Delay: {1}, Number of workers: {2}.\n'
      ' To exit press CTRL+C'.format(routing_key, callback_delay, worker_number))


def callback(ch, method, properties, body):
    global task_counter
    client_message = json.loads(body)
    print(' [x] Received: %s, message_type: %s, routing_key: %s'
          % (client_message, type(client_message), method.routing_key))
    if callback_delay:
        time.sleep(callback_delay)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print('DONE TASK: {}'.format(task_counter))
    task_counter += 1

channel.basic_consume(callback, queue=queue_name)
channel.start_consuming()
