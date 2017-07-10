# -*- coding: utf-8 -*-
import pika
import json
import time
import sys


from elizabeth import Text
from random import choice

SERVER_LIST = ['s_1', 's_2', 's_3']

conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = conn.channel()
channel.exchange_declare(exchange='direct_message', exchange_type='direct')


def send_msg(payload, routing_key):
    channel.basic_publish(exchange='direct_message', routing_key=routing_key, body=payload)
    print('[x] Send: %s, message_type: %s, routing_key: %s' % (payload, type(payload),
                                                               routing_key))


def main():
    try:
        client_msg = Text()
        payload = dict(message=None, msg_id=0)
        msg_count = 1
        while True:
            payload['message'] = client_msg.sentence()
            payload['msg_id'] = msg_count
            send_msg(json.dumps(payload), choice(SERVER_LIST))
            msg_count += 1
            time.sleep(1)
    except KeyboardInterrupt:
        conn.close()
        sys.exit()

if __name__ == '__main__':
    main()