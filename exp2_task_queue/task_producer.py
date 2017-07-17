# -*- coding: utf-8 -*-
import pika
import json
import time
import sys


from elizabeth import Text

conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = conn.channel()
channel.queue_declare(queue='task_queue', durable=True)


def send_msg(payload):
    channel.basic_publish(exchange='',
                          routing_key='task_queue',
                          body=payload,
                          properties=pika.BasicProperties(
                              delivery_mode=2,  # make message persistent
                          ))
    print(' [x] Send: {0}, message_type: {1}'.format(payload, type(payload)))


def main():
    try:
        client_msg = Text()
        payload = dict(message=None, msg_id=0, producer_type='SYNC')
        msg_count = 1
        while True:
            payload['message'] = client_msg.sentence()
            payload['msg_id'] = msg_count
            send_msg(json.dumps(payload))
            msg_count += 1
            time.sleep(1)
    except KeyboardInterrupt:
        conn.close()
        sys.exit()

if __name__ == '__main__':
    main()
