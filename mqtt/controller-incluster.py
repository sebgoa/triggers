#!/usr/bin/env python
"""A controller """

import json
import logging
import os
import time
import httplib
import sys
import requests

from kubernetes import client, config
from kubernetes.client.rest import ApiException
import crd

from multiprocessing import Process
import paho.mqtt.client as mqtt

GROUP = "kubeless.io"
VERSION = "v1beta1"
PLURAL = "mqtttriggers"

config.load_incluster_config()

v1 = client.CoreV1Api()
crds = client.CustomObjectsApi()

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
    
    def topic(self):
        return self._spec["topic"]
                
    def functions(self):
        return self._spec["functionSelector"]["matchLabels"]

def get_mappings():
    try: 
        mappings = crds.list_cluster_custom_object(GROUP, VERSION, PLURAL)
    except ApiException as e:
        print("Exception when calling CustomObjectsApi->list_cluster_custom_object: %s\n" % e)
    return mappings['items']

def get_functions(selector):
    try: 
        functions = crds.list_cluster_custom_object(GROUP, VERSION, 'functions', label_selector=selector)
    except ApiException as e:
        print("Exception when calling CustomObjectsApi->list_cluster_custom_object: %s\n" % e)
    return functions['items']
    
def create_selector(func_selectors):
    selector = []
    for keys in func_selectors.keys():
        selector.append(keys + '=' + func_selectors[keys])
    return ",".join(selector)

def event2func(topic, func_selectors):
    
    def callback(message):
        sys.stdout = open(str(os.getpid()) + ".out", "a", buffering=0)
        sys.stderr = open(str(os.getpid()) + "_error.out", "a", buffering=0)
        print message
        # TODO: Add error handling for svc selection and post requests
    
        services = v1.list_service_for_all_namespaces(label_selector=create_selector(func_selectors))
        for svc in services.items:
            svc_url = 'http://%s.%s:%s' % (svc.metadata.name, svc.metadata.namespace, str(svc.spec.ports[0].port))
            requests.post(svc_url, data=message.payload)
    
    sys.stdout = open(str(os.getpid()) + ".out", "a", buffering=0)
    sys.stderr = open(str(os.getpid()) + "_error.out", "a", buffering=0)
        
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe(topic)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        callback(msg)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    broker_address = os.getenv("BROKER_ADDRESS", "mqtt")
    broker_port = os.getenv("BROKER_PORT", 1883)

    client.connect(broker_address, broker_port, 60)

    client.loop_forever()

def create_meta(trigger):
    topic = trigger.topic()
    functions = trigger.functions()
    p = Process(target=event2func, args=(topic, functions,))
    p.start()
    return p
        
def update_meta(trigger):
    try:
        p = create_meta(trigger)
    except ApiException as e:
        if e.status != httplib.CONFLICT:
            raise e
    return p
        
def delete_meta(name, pid):
    for p in pid:
        logging.warning("check name %s and pid %s" % (p[0],str(p[1])))
        if p[0] == name:
            p[1].terminate()
            p[1].join()
    logging.warning("Deleted the CloudStorage Trigger")

def process_meta(t, trigger, pid):
    if t == "DELETED":
        delete_meta(trigger.crd_name(), pid)
        logging.warning("Deleted CRD, check garbage collection")
    elif t in ["MODIFIED", "ADDED"]:
        p = update_meta(trigger)
        pid.append((trigger.crd_name(), p))
    else:
        logging.error("Unrecognized event type: %s", t)
    
def main():
    
    pid = []
    
    # TODO: create initialization step
    for mapping in get_mappings():
        process_meta("ADDED", Trigger(mapping), pid)
    
    resource_version = ""
    while True:
        try:
            stream = crd.Watch().stream(crds.list_cluster_custom_object,
                                          GROUP, VERSION, PLURAL,
                                          resource_version=resource_version)
        except ApiException as e:
            print "Exception when calling CustomObjectsApi->list_cluster_custom_object: %s\n" % e
                       
        for event in stream:
            try:
                t = event["type"]
                obj = event["object"]
                trigger = Trigger(obj)
                logging.warning("Trigger %s, %s" % (trigger.crd_name(),t))  
                process_meta(t, trigger, pid)

                # Configure where to resume streaming.
                metadata = obj.get("metadata")
                if metadata:
                    resource_version = metadata['resourceVersion']
                    #resource_version = crds.list_cluster_custom_object(GROUP, VERSION, PLURAL)["metadata"]["resourceVersion"]
            except:
                logging.exception("Error handling event")

if __name__ == "__main__":
    main()
