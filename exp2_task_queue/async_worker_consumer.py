# -*- coding: utf-8 -*-
"""
    Simple task consumer(worker) example implementation using aioamqp.
"""

import asyncio
import aioamqp
import functools
import json
import os
import signal

from optparse import OptionParser


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
    options, args = parser.parse_args()

    return options

opt = parse_args_for_init_worker()
callback_delay = opt.callback_delay
worker_number = opt.worker_number
task_counter = 1


async def callback(channel, body, envelope, properties):
    global task_counter
    client_message = json.loads(body)
    print(' [x] Received: {0}, message_type: {1}'.
          format(client_message, type(client_message)))
    if callback_delay:
        await asyncio.sleep(task_counter)

    await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)
    print('DONE TASK: {}'.format(task_counter))
    task_counter += 1


async def receive_worker():
    try:
        transport, protocol = await aioamqp.connect('localhost', 5672)
        channel = await protocol.channel()
        await channel.queue(queue_name='task_queue', durable=True)
        await channel.basic_qos(prefetch_count=1, connection_global=False)
        await channel.basic_consume(callback, queue_name='task_queue')
    except aioamqp.AmqpClosedConnection:
        print("closed connections")
        return


def main():

    def ask_exit(signame):
        print("got signal %s: exit" % signame)
        loop.stop()

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame))

    print(' [*] Waiting for messages. Delay:{0}, Number of workers: {1}.\n'
          ' Press CTRL+C or send SIGINT or SIGTERM to exit. PID: {2}'.
          format(callback_delay, worker_number, os.getpid()))
    try:
        loop.run_until_complete(receive_worker())
        loop.run_forever()
    finally:
        loop.close()

if __name__ == '__main__':
    main()

