#!/usr/bin/env python

import os
import boto3

aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

sqs = boto3.resource('sqs', region_name='us-east-1')
squeue = sqs.get_queue_by_name(QueueName='kubeless.fifo')

response = squeue.send_message(
    MessageBody='flynn',
    MessageGroupId='messageGroup1'
)

# Th response is NOT a resource, but gives you a message ID and MD5
print(response.get('MessageId'))
print(response.get('MD5OfMessageBody'))

