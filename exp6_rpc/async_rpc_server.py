# -*- coding: utf-8 -*-
"""
    RPC server, aioamqp implementation of RPC examples
"""
import asyncio
import aioamqp

async def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return await fib(n - 1) + await fib(n - 2)

async def on_request(channel, body, envelope, properties):
    try:
        fib_num = int(body)
        print(" [.] Run command: fib(%s)" % fib_num)
        response = await fib(fib_num)
        await channel.basic_publish(payload=str(response), exchange_name='',
                                    routing_key=properties.reply_to,
                                    properties={'correlation_id': properties.correlation_id})
    except ValueError as e:
        print('Input wrong fibonacci num: {0}. Error: {1}'.format(fib_num, e))
    await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)

async def async_rpc_server():
    try:
        transport, protocol = await aioamqp.connect()
        channel = await protocol.channel()
        await channel.queue_declare(queue_name='rpc_queue')
        await channel.basic_qos(prefetch_count=1, prefetch_size=0, connection_global=False)
        await channel.basic_consume(on_request, queue_name='rpc_queue')
        print(" [x] Awaiting RPC requests")
    except aioamqp.AmqpClosedConnection:
        print("closed connections")
        return
    except KeyboardInterrupt:
        await protocol.close()
        transport.close()


def main():
    tasks = asyncio.gather(async_rpc_server())
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(tasks)
        loop.run_forever()
    except KeyboardInterrupt:
        print("/nCaught keyboard interrupt. Canceling tasks...")
        tasks.cancel()
    finally:
        loop.close()

if __name__ == '__main__':
    main()
