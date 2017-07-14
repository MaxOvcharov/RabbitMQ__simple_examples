# -*- coding: utf-8 -*-
"""
    Simple send producer example implementation using aioamqp.
"""
import aioamqp
import asyncio
import functools
import json
import os
import signal

from elizabeth import Text


@asyncio.coroutine
def send_msg(payload, channel):
    print(' [x] Send: {0}, message_type: {1}'.format(payload, type(payload)))
    yield from channel.basic_publish(payload=payload, exchange_name='',
                                     routing_key='client_msg_queue')


@asyncio.coroutine
def send():
    try:
        client_msg = Text()
        payload = dict(message=None, msg_id=0)
        msg_count = 1

        transport, protocol = yield from aioamqp.connect()
        channel = yield from protocol.channel()
        yield from channel.queue_declare(queue_name='client_msg_queue')
        while True:
            payload['message'] = client_msg.sentence()
            payload['msg_id'] = msg_count
            yield from send_msg(json.dumps(payload), channel)
            msg_count += 1
            yield from asyncio.sleep(3)
    except KeyboardInterrupt:
        yield from protocol.close()
        transport.close()


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
        loop.run_until_complete(send())
        loop.run_forever()
    finally:
        loop.close()

if __name__ == '__main__':
    main()

