# -*- coding: utf-8 -*-
"""
    Simple send consumer example implementation using aioamqp.
"""

import asyncio
import aioamqp
import functools
import json
import os
import signal


async def callback(channel, body, envelope, properties):
    client_message = json.loads(body.decode('utf-8'))
    print(' [x] Received: {0}, message_type: {1}'.format(client_message,
                                                         type(client_message)))


async def receive():
    transport, protocol = await aioamqp.connect()
    channel = await protocol.channel()

    await channel.queue_declare(queue_name='client_msg_queue')

    await channel.basic_consume(callback, queue_name='client_msg_queue', no_ack=True)


def main():

    def ask_exit(signame):
        print("got signal %s: exit" % signame)
        loop.stop()

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame))

    print("Event loop running forever, press Ctrl+C to interrupt.")
    print("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())
    try:
        loop.run_until_complete(receive())
        loop.run_forever()
    finally:
        loop.close()

if __name__ == '__main__':
    main()
