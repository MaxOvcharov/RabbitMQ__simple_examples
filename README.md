### RabbitMQ_examples
#### Simple examples with different RabbitMQ modes

##### Example №1 - Simple RabbitMQ example
###### SYNC mode
First run consumer:
```bash
python receive_consumer.py
```
Than run producer:
```bash
python send_producer.py
```
###### ASYNC mode
First run async consumer:
```bash
python async_receive_consumer.py
```
Than run async producer:
```bash
python async_send_producer.py
```
##### Example №2 - Task RabbitMQ example
###### SYNC mode
First run tasks consumer:
```bash
python worker_consumer.py
```
Than run task producer:
```bash
python task_producer.py
```
###### ASYNC mode
First run async task consumer:
```bash
python async_worker_consumer.py
```
Than run async task producer:
```bash
python async_task_producer.py
```
##### Example №3 - PUB/SUB RabbitMQ mode
###### SYNC mode
First run subscriber worker:
```bash
python sub_consumer.py
```
Than run publisher worker:
```bash
python pub_producer.py
```
###### ASYNC mode
First run async subscriber worker:
```bash
python async_sub_consumer.py
```
Than run async publisher worker:
```bash
python async_pub_producer.py
```
##### Example №4 - DIRECT ROUTING RabbitMQ mode
###### SYNC mode
First run consumer worker with direct routing:
```bash
python direct_consumer.py -k 2
```
Than run producer worker with direct routing:
```bash
python direct_producer.py
```
###### ASYNC mode
First run async consumer worker with direct routing:
```bash
python async_direct_consumer.py -k 1
```
Than run async producer worker with direct routing:
```bash
python async_direct_producer.py
```
##### Example №5 - TOPIC ROUTING RabbitMQ mode
###### SYNC mode
First run consumer worker with topic routing:
```bash
python topic_consumer.py -k s1 '*'
```
Than run producer worker with topic routing:
```bash
python topic_producer.py
```
###### ASYNC mode


### ============== Installing RabbitMQ ===============

1) Updating system's default application toolset:
```bash
apt-get update
apt-get -y upgrade
```
2) Enable RabbitMQ application repository:
```bash
echo "deb http://www.rabbitmq.com/debian/ testing main" >> /etc/apt/sources.list
```
3) Add the verification key for the package:
```bash
curl http://www.rabbitmq.com/rabbitmq-signing-key-public.asc | sudo apt-key add -
```
4) Update the sources with our new addition from above:
```bash
apt-get update
```
5) install RabbitMQ:
```bash
sudo apt-get install rabbitmq-server
```
6) In order to manage the maximum amount of connections upon launch, 
   open up and edit the following configuration file 
   (Uncomment the limit line (i.e. remove #) before saving):
```bash
sudo vim /etc/default/rabbitmq-server
```

### ======== Enabling the Management Console =========

1) Enable RabbitMQ Management Console
```bash
sudo rabbitmq-plugins enable rabbitmq_management
```
2) Run RabbitMQ Management Console on brouser
   The default username and password are both set “guest” for the log in.
```bash
http://localhost:15672/
```

### ============== Managing RabbitMQ =================

1) To start the service:
```bash
service rabbitmq-server start
```
2) To stop the service:
```bash
service rabbitmq-server stop
```
3) To restart the service:
```bash
service rabbitmq-server restart
```
4) To check the status:
```bash
service rabbitmq-server status
```

### == How to Create a Cluster On a Single Machine ===

1) Checkout to superuser:
```bash
sudo -i
```
2) Make sure that you don’t have a rabbitmq.config:

```bash
ls -lah /etc/rabbitmq/rabbitmq.config
```
3) Create new RabbitMQ node:
```bash
RABBITMQ_NODE_PORT=5673 RABBITMQ_SERVER_START_ARGS="-rabbitmq_management listener [{port,15673}]" RABBITMQ_NODENAME=<YOUR_NODE_NAME> rabbitmq-server
```
4) Check node status:  
```bash
rabbitmqctl -n <YOUR_NODE_NAME> status
```
5) Stop RabbitMQ node:
```bash 
rabbitmqctl -n <YOUR_NODE_NAME> stop_app
```
6) Run RabbitMQ node:
```bash
rabbitmqctl -n <YOUR_NODE_NAME> reset
```
7) Join new node to the exist RabbitMQ cluster:
```bash
rabbitmqctl -n <YOUR_NODE_NAME> join_cluster rabbit@`hostname -s`
```
8) Start RabbitMQ node:
```bash
rabbitmqctl -n <YOUR_NODE_NAME> start_app
```
9) Check RabbitMQ cluster status:
```bash
rabbitmqctl cluster_status
```
