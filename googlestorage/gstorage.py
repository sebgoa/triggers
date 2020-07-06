import os
import json
from datetime import datetime, timezone

from cloudevents.sdk import converters
from cloudevents.sdk import marshaller
from cloudevents.sdk.converters import structured
from cloudevents.sdk.event import v1

from google.cloud import pubsub_v1

import requests

subscriber = pubsub_v1.SubscriberClient()

subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
    project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
    sub=os.getenv('MY_SUBSCRIPTION_NAME'),
)

K_SINK = os.getenv('K_SINK')

m = marshaller.NewHTTPMarshaller([structured.NewJSONHTTPCloudEventConverter()])

def run_structured(event, url):
    structured_headers, structured_data = m.ToRequest(
        event, converters.TypeStructured, json.dumps
    )
    print("structured CloudEvent")
    print(structured_data.getvalue())

    response = requests.post(url,
                             headers=structured_headers,
                             data=structured_data.getvalue())
    response.raise_for_status()

def callback(message):
    e = {"event": json.dumps(message.data.decode("utf-8"))}
    local_time = datetime.now(timezone.utc).astimezone()
    event = (
        v1.Event()
        .SetContentType("application/json")
        .SetData(e)
        .SetEventID("my-id")
        .SetSource("from-galaxy-far-far-away")
        .SetEventTime(local_time.isoformat())
        .SetEventType("com.google.cloudstorage")
        .SetExtensions("")
    )
    print(message.data)
    res = run_structured(event, K_SINK)

    message.ack()

future = subscriber.subscribe(subscription_name, callback)

try:
    future.result()
except KeyboardInterrupt:
    future.cancel()




