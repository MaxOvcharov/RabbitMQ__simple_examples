# -*- coding: utf-8 -*-
"""
    Simple consumer example with 'direct' routing implementation using pika
"""
import json
import pika
import time
import sys

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
    parser.add_option('-k', '--routing_key', dest='routing_key',
                      help='CHOSE INDEX(STARTS FROM 1) OF ROUTING '
                           'KEY FROM SERVER_LIST = {}'.format(SERVER_LIST),
                      type='int', default=0)
    options, args = parser.parse_args()
    if not options.routing_key:
        parser.error('Routing key is mandatory for running worker. Example: --routing_key 1,'
                     ' choose the first routing_key from SERVER_LIST= {}'.format(SERVER_LIST))

    return options

opt = parse_args_for_init_worker()
callback_delay = opt.callback_delay
routing_key = SERVER_LIST[opt.routing_key - 1]
task_counter = 1

conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = conn.channel()
channel.exchange_declare(exchange='direct_message', exchange_type='direct')
res = channel.queue_declare(exclusive=True)
queue_name = res.method.queue
channel.queue_bind(exchange='direct_message', queue=queue_name, routing_key=routing_key)
print(' [*] Waiting for messages. Routing key: {0}, Delay: {1}.\n'
      ' To exit press CTRL+C'.format(routing_key, callback_delay))


def callback(ch, method, properties, body):
    global task_counter
    client_message = json.loads(body.decode('utf-8'))
    print(' [x] Received: {0}, message_type: {1}, routing_key: {2}'
          .format(client_message, type(client_message), method.routing_key))
    if callback_delay:
        time.sleep(callback_delay)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print('DONE TASK: {}'.format(task_counter))
    task_counter += 1


def main():
    try:
        channel.basic_consume(callback, queue=queue_name)
        channel.start_consuming()
    except KeyboardInterrupt:
        conn.close()
        sys.exit()

if __name__ == '__main__':
    main()
