# -*- coding: utf-8 -*-
"""
    Simple consumer example with 'topic' routing implementation using pika
"""
import json
import pika
import time
import sys

from optparse import OptionParser

SERVER_LIST = ['s1', 's2', 's3', '*', '#']
MSG_TYPE = ['sendMessage', 'sendHistory', 'sendCallback', '*', '#']


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
                      help='CREATE ROUTING KEY WITH VALUE FROM SERVER_LIST = {0}'
                           ' AND VALUE FROM MSG_TYPE = {1}'.format(SERVER_LIST, MSG_TYPE),
                      nargs=2, type='string')
    options, args = parser.parse_args()
    if not options.routing_key:
        parser.error('\nRouting key is mandatory for running worker.\n'
                     'For example: -k s1.sendMessage \n'
                     'You can use:\n1) * (star) can substitute for exactly one word; \n'
                     '2) # (hash) can substitute for zero or more words. \n'
                     'For more information use --help')
    elif options.routing_key[0] not in SERVER_LIST or options.routing_key[1] not in MSG_TYPE:
        parser.error('Some of the values in routing_key is wrong. '
                     '\nSERVER: %s, MSG_TYPE: %s' % options.routing_key)

    return options

opt = parse_args_for_init_worker()
callback_delay = opt.callback_delay
routing_key = '.'.join(opt.routing_key)
task_counter = 1

conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = conn.channel()
channel.exchange_declare(exchange='topic_message', exchange_type='topic')
res = channel.queue_declare(exclusive=True)
queue_name = res.method.queue
channel.queue_bind(exchange='topic_message', queue=queue_name, routing_key=routing_key)
print(' [*] Waiting for messages. Routing key: {0}, Delay: {1}.\n'
      ' To exit press CTRL+C'.format(routing_key, callback_delay))


def callback(ch, method, properties, body):
    global task_counter
    client_message = json.loads(body)
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
