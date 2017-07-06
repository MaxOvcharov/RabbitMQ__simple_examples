# -*- coding: utf-8 -*-
import pika
import json

conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = conn.channel()
channel.queue_declare(queue='client_msg_queue')

print(' [*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    client_message = json.loads(body)
    print(' [x] Received: %s, message_type: %s' % (client_message,
                                                   type(client_message)))

channel.basic_consume(callback, queue='client_msg_queue', no_ack=True)
channel.start_consuming()
