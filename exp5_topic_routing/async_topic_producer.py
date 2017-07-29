#!/usr/bin/env python
"""
    Simple producer example with 'topic' routing implementation using pika
"""

import asyncio
import aioamqp
import json

from elizabeth import Text
from random import choice

SERVER_LIST = ['s1', 's2', 's3']
MSG_TYPE = ['sendMessage', 'sendHistory', 'sendCallback']

async def send_topic_msg(payload, channel, routing_key):
    await channel.basic_publish(payload, exchange_name='topic_message',
                                routing_key=routing_key)
    print(' [x] Send direct message: {0}, message_type: {1}, routing_key: {2}'.
          format(payload, type(payload), routing_key))

async def topic_pub_worker():
    try:
        client_msg = Text()
        payload = dict(message=None, msg_id=0, producer_type='ASYNC')
        msg_count = 1
        transport, protocol = await aioamqp.connect('localhost', 5672)
        channel = await protocol.channel()
        await channel.exchange_declare(exchange_name='topic_message', type_name='topic')
        while True:
            payload['message'] = client_msg.sentence()
            payload['msg_id'] = msg_count
            routing_key = choice(SERVER_LIST) + '.' + choice(MSG_TYPE)
            await send_topic_msg(json.dumps(payload), channel, routing_key)
            msg_count += 1
            await asyncio.sleep(1)
    except aioamqp.AmqpClosedConnection:
        print("closed connections")
        return
    except KeyboardInterrupt:
        await protocol.close()
        transport.close()


def main():
    tasks = asyncio.gather(topic_pub_worker())
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
