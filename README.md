# RabbitMQ_examples
## Simple examples with different RabbitMQ modes

### Example №1 - Simple RabbitMQ example
#### SYNC mode

#### ASYNC mode

### Example №2 - Task RabbitMQ example
#### SYNC mode

#### ASYNC mode

### Example №3 - PUB/SUB RabbitMQ mode
#### SYNC mode

#### ASYNC mode

### How to Create a Cluster On a Single Machine

1) sudo -i
2) Make sure that you don’t have a /etc/rabbitmq/rabbitmq.config
3) RABBITMQ_NODE_PORT=5673 RABBITMQ_SERVER_START_ARGS="-rabbitmq_management listener [{port,15673}]" RABBITMQ_NODENAME=<YOUR_NODE_NAME> rabbitmq-server
4) rabbitmqctl -n <YOUR_NODE_NAME> status
5) rabbitmqctl -n <YOUR_NODE_NAME> stop_app
6) rabbitmqctl -n <YOUR_NODE_NAME> reset
7) rabbitmqctl -n <YOUR_NODE_NAME> join_cluster rabbit@`hostname -s`
8) rabbitmqctl -n <YOUR_NODE_NAME> start_app
9) rabbitmqctl cluster_status