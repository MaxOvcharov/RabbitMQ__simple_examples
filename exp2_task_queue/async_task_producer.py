# -*- coding: utf-8 -*-
"""
    Simple queue task producer example implementation using aioamqp.
"""
import aioamqp
import asyncio
import json

from elizabeth import Text


async def send_msg(payload, channel):
    print(' [x] Send: {0}, message_type: {1}'.format(payload, type(payload)))
    await channel.basic_publish(payload=payload, exchange_name='',
                                routing_key='task_queue',
                                properties={'delivery_mode': 2})


async def send_worker():
    try:
        client_msg = Text()
        payload = dict(message=None, msg_id=0, producer_type='ASYNC')
        msg_count = 1
        transport, protocol = await aioamqp.connect('localhost', 5672)
        channel = await protocol.channel()
        await channel.queue('task_queue', durable=True)
        while True:
            payload['message'] = client_msg.sentence()
            payload['msg_id'] = msg_count
            await send_msg(json.dumps(payload), channel)
            msg_count += 1
            await asyncio.sleep(0.003)
    except aioamqp.AmqpClosedConnection:
        print("closed connections")
        return
    except KeyboardInterrupt:
        await protocol.close()
        transport.close()


def main():
    tasks = asyncio.gather(send_worker())
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

