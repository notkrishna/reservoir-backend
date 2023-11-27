# celeryconfig.py

# RabbitMQ Broker Configuration
broker_url = 'amqp://kris:krispar@1@localhost:5672/myvhost'

# Result Backend Configuration
result_backend = 'rpc://'

# Task Serialization Configuration
accept_content = ['application/json']
result_serializer = 'json'
task_serializer = 'json'
