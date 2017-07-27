#!/usr/bin/env python
"""
    Simple consumer example with 'topic' routing implementation using pika
"""
import asyncio
import aioamqp
import functools
import json
import os
import signal

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

async def callback(channel, body, envelope, properties):
    global task_counter
    client_message = json.loads(body)
    print(' [x] Received: {0}, message_type: {1}, routing_key: {2}'
          .format(client_message, type(client_message), envelope.routing_key))
    if callback_delay:
        await asyncio.sleep(task_counter)
    print('DONE TASK: {}'.format(task_counter))
    task_counter += 1


async def direct_sub_worker():
    try:
        transport, protocol = await aioamqp.connect('localhost', 5672)
        channel = await protocol.channel()
        await channel.exchange('topic_message', 'topic')
        result = await channel.queue(queue_name='', durable=False, auto_delete=True)
        queue_name = result['queue']
        await channel.queue_bind(exchange_name='topic_message', queue_name=queue_name,
                                 routing_key=routing_key)
        await channel.basic_consume(callback, queue_name=queue_name)
    except aioamqp.AmqpClosedConnection:
        print("closed connections")
        return
    except KeyboardInterrupt:
        await protocol.close()
        transport.close()


def main():
    def ask_exit(signame):
        print("got signal %s: exit" % signame)
        loop.stop()

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame))

    print(' [*] Waiting for messages. Delay:{0}.\n'
          ' Press CTRL+C or send SIGINT or SIGTERM to exit. PID: {1}'.
          format(callback_delay, os.getpid()))
    try:
        loop.run_until_complete(direct_sub_worker())
        loop.run_forever()
    finally:
        loop.close()

if __name__ == '__main__':
    main()
