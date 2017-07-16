# -*- coding: utf-8 -*-
"""
    Simple send producer example implementation using aioamqp.
"""
import aioamqp
import asyncio
import json

from elizabeth import Text


@asyncio.coroutine
def send_msg(payload, channel):
    print(' [x] Send: {0}, message_type: {1}'.format(payload, type(payload)))
    yield from channel.basic_publish(payload=payload, exchange_name='',
                                     routing_key='client_msg_queue')


@asyncio.coroutine
def worker():
    try:
        client_msg = Text()
        payload = dict(message=None, msg_id=0, producer_type='ASYNC')
        msg_count = 1

        transport, protocol = yield from aioamqp.connect()
        channel = yield from protocol.channel()
        yield from channel.queue_declare(queue_name='client_msg_queue')
        while True:
            payload['message'] = client_msg.sentence()
            payload['msg_id'] = msg_count
            yield from send_msg(json.dumps(payload), channel)
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
    tasks = asyncio.gather(asyncio.async(worker()))
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(tasks)
        loop.run_forever()
    except KeyboardInterrupt as e:
        print("Caught keyboard interrupt. Canceling tasks...")
        tasks.cancel()
        loop.run_forever()
        tasks.exception()
    finally:
        loop.close()

if __name__ == '__main__':
    main()

