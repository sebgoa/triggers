#!/usr/bin/env python

import os
import requests

from google.cloud import pubsub_v1

from cloudevents.sdk import converters
from cloudevents.sdk import marshaller
from cloudevents.sdk.converters import structured
from cloudevents.sdk.event import v01

channel = os.environ['CHANNEL']
namespace = os.environ['NAMESPACE']
gcp_project = os.environ['PROJECT']
gcs_subscription = os.environ['SUBSCRIPTION']

sub = pubsub_v1.SubscriberClient()

sub_name = 'projects/%s/subscriptions/%s' % (gcp_project, gcs_subscription)

def callback(message):
    print(message.data)
    url = 'http://%s-channel.%s.svc.cluster.local' % (channel, namespace)
    print(url)

    event = (
        v01.Event().
        WithContentType("application/json").
        WithData(message.data).
        WithEventID("my-id").
        WithSource("from-galaxy-far-far-away").
        WithEventTime("tomorrow").
        WithEventType("cloudevent.greet.you")
    )
    m = marshaller.NewHTTPMarshaller(
        [
            structured.NewJSONHTTPCloudEventConverter(type(event))
        ]
    )

    headers, body = m.ToRequest(event, converters.TypeStructured, lambda x: x)

    requests.post(url, data=body, headers=headers)
    message.ack()

future = sub.subscribe(sub_name, callback)
future.result()
