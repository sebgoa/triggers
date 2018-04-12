#!/usr/bin/env python
"""A controller """

import json
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import logging
import os
import time
import httplib

from multiprocessing import Process
from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()

GROUP = "kubeless.io"
VERSION = "v1beta1"
PLURAL = "cloudstoragetriggers"

class Trigger(object):
    def __init__(self, obj):
        self._obj = obj
        self._apiversion = obj["apiVersion"]
        self._kind = obj["kind"]
        self._metadata = obj["metadata"]
        self._spec = obj["spec"]
        
    def crd_name(self):
        return self._metadata["name"]
            
    def any_versions(self):
        return "name=" + self.crd_name()
    
    def subscription(self):
        return self._spec["subscription"]
        
    def project(self):
        return self._spec["project"]
        
    def functions(self):
        return self._spec["functionSelector"]["matchLabels"]

def callback(message):
    print message
    message.ack()

def cloudstorage(subscription, project, functions):
    name = 'projects/' + project + '/subscriptions/' + subscription
    listener = subscriber.subscribe(name)
    
    future = listener.open(callback)
    future.result()

def create_meta(trigger):
    subscription = trigger.subscription()
    functions = trigger.functions()
    project = trigger.project()
    p = Process(target=cloudstorage, args=(subscription, project, functions,))
    p.start()
    print subscription
    print functions
    print project
    logging.warning("BlaBlah")
        
def update_meta(trigger):
    try:
        create_meta(trigger)
    except ApiException as e:
        if e.status != httplib.CONFLICT:
            raise e

        # Tear down any versions that shouldn't exist.
        #delete_meta(app.other_versions())
        
def delete_meta(selector):
    logging.warning("Deleted the CloudStorage Trigger")

def process_meta(t, trigger, obj):
    if t == "DELETED":
        delete_meta(trigger.any_versions())
        logging.warning("Deleted CRD, check garbage collection")
    elif t in ["MODIFIED", "ADDED"]:
        update_meta(trigger)
    else:
        logging.error("Unrecognized type: %s", t)
    
def main():
    #config.load_incluster_config()
    config.load_kube_config()

    apps_beta1 = client.AppsV1beta1Api()
    crds = client.CustomObjectsApi()
    v1 = client.CoreV1Api()
    
    resource_version = ""
    while True:
        try:
            print resource_version
            stream = watch.Watch().stream(crds.list_cluster_custom_object,
                                          GROUP, VERSION, PLURAL,
                                          resource_version=resource_version)
            print "in event loop with " + resource_version
        except ApiException as e:
            print "Exception when calling CustomObjectsApi->list_cluster_custom_object: %s\n" % e
                       
        for event in stream:
            try:
                t = event["type"]
                obj = event["object"]
                trigger = Trigger(obj)
                logging.warning("Trigger %s, %s" % (trigger.crd_name(),t))  
                #process_meta(t, trigger, obj)

                # Configure where to resume streaming.
                metadata = obj.get("metadata")
                if metadata:
                    resource_version = metadata['resourceVersion']
                    print resource_version
            except:
                logging.exception("Error handling event")

if __name__ == "__main__":
    main()
