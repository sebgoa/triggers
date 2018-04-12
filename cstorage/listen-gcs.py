#!/usr/bin/env python

from google.cloud import pubsub_v1

sub = pubsub_v1.SubscriberClient()

#topic = 'project/skippbox/topics/barfoo'
sub_name = 'projects/skippbox/subscriptions/carogoasub'
subscription = sub.subscribe(sub_name)

def callback(message):
    print message
    message.ack()

future = subscription.open(callback)
future.result()
