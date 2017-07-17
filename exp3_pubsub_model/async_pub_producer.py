# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Simple async pub/sub example
"""

import asyncio
import aioamqp
import json

from elizabeth import Text


@asyncio.coroutine
def send_log_msg(payload, channel):
    print(' [x] Send log message: {0}, message_type: {1}'.format(payload, type(payload)))
    yield from channel.basic_publish(payload, exchange_name='logs', routing_key='')


@asyncio.coroutine
def pub_worker():
    try:
        client_msg = Text()
        payload = dict(message=None, msg_id=0, producer_type='ASYNC')
        msg_count = 1
        transport, protocol = yield from aioamqp.connect('localhost', 5672)
        channel = yield from protocol.channel()
        yield from channel.exchange_declare(exchange_name='logs', type_name='fanout')
        while True:
            payload['message'] = client_msg.sentence()
            payload['msg_id'] = msg_count
            yield from send_log_msg(json.dumps(payload), channel)
            msg_count += 1
            yield from asyncio.sleep(0.003)
    except aioamqp.AmqpClosedConnection:
        print("closed connections")
        return
    except KeyboardInterrupt:
        yield from protocol.close()
        transport.close()


def main():
    # Side note: Apparently, async() will be deprecated in 3.4.4.
    # See: https://docs.python.org/3.4/library/asyncio-task.html#asyncio.async
    tasks = asyncio.gather(asyncio.async(pub_worker()))
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(tasks)
        loop.run_forever()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt. Canceling tasks...")
        tasks.cancel()
        loop.run_forever()
        tasks.exception()
    finally:
        loop.close()

if __name__ == '__main__':
    main()

