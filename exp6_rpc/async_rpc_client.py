#!/usr/bin/env python

"""
    RPC client, aioamqp implementation of RPC examples.
"""
import asyncio
import aioamqp
import uuid


class FibonacciRpcClient(object):
    def __init__(self):
        self.transport = None
        self.protocol = None
        self.channel = None
        self.callback_queue = None
        self.response = None
        self.corr_id = None
        self.waiter = asyncio.Event()

    async def connect(self):
        self.transport, self.protocol = await aioamqp.connect()
        self.channel = await self.protocol.channel()

        result = await self.channel.queue_declare(queue_name='', exclusive=True)
        self.callback_queue = result['queue']

        await self.channel.basic_consume(self.on_response, no_ack=True,
                                         queue_name=self.callback_queue)

    async def on_response(self, channel, body, envelope, properties):
        if self.corr_id == properties.correlation_id:
            self.response = body
        self.waiter.set()

    async def call(self, n):
        if not self.protocol:
            await self.connect()
        self.response = None
        self.corr_id = str(uuid.uuid4())
        await self.channel.basic_publish(payload=str(n), exchange_name='',
                                         routing_key='rpc_queue',
                                         properties={
                                             'reply_to': self.callback_queue,
                                             'correlation_id': self.corr_id})
        await self.waiter.wait()
        await self.protocol.close()
        return int(self.response)


async def async_rpc_client():
    fibonacci_rpc = FibonacciRpcClient()
    while True:
        fib_num = input('Enter Fibonacci number: ')
        print(' [x] Run remote command: fib(%s)' % fib_num)
        res = await fibonacci_rpc.call(30)
        print(' [.] Got result from remote server: %r' % res)


def main():
    tasks = asyncio.gather(async_rpc_client())
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(tasks)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt. Canceling tasks...")
        tasks.cancel()
        loop.run_forever()
        tasks.exception()
    finally:
        loop.close()

if __name__ == '__main__':
    main()
