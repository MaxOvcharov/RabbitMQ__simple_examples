# -*- coding: utf-8 -*-
import json
import pika
import sys

conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = conn.channel()
channel.queue_declare(queue='client_msg_queue')


def callback(ch, method, properties, body):
    client_message = json.loads(body.decode('utf-8'))
    print(' [x] Received: {0}, message_type: {1}'.format(client_message,
                                                         type(client_message)))


def main():
    try:
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.basic_consume(callback, queue='client_msg_queue', no_ack=True)
        channel.start_consuming()
    except KeyboardInterrupt:
        conn.close()
        sys.exit()

if __name__ == '__main__':
    main()
