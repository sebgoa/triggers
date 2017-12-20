#!/usr/bin/env python
"""A controller """

import sys

from kubernetes import client, config, watch
import logging
import boto3

class Ingress(object):
    def __init__(self, obj):
        self._obj = obj
        self._apiversion = obj.api_version
        self._kind = obj.kind
        self._metadata = obj.metadata
        self._spec = obj.spec

    def ing_name(self):
        return self._metadata.name

    def ing_route(self):
        return self._spec.rules[0].host

def main():
    # config.load_incluster_config()
    config.load_kube_config()

    ext_beta1 = client.ExtensionsV1beta1Api()

    aws = boto3.client('apigateway', region_name='us-east-1')
    
    for apis in aws.get_rest_apis()['items']:
        if apis['name'] == 'kubeless':
            apiid = apis['id']

    # res = aws.create_rest_api(name='kubeless', description='this is a kubeless test')
    #apiid = res['id']

    # get the resources root id
    rootid = aws.get_resources(restApiId=apiid)['items'][0]['id']

    def process_meta(t, ing, apiid, rootid):
        if t == "DELETED":
            logging.warning("ingress %s has been deleted", ing.ing_name())
            
            resources = aws.get_resources(restApiId=apiid)
            for resource in resources['items']:
                path = '/' + ing.ing_name()
                if resource['path'] == path:
                    res = aws.delete_resource(restApiId=apiid, resourceId=resource['id'])
            # process_delete(ing)
        elif t == "MODIFIED":
            logging.warning("ingress %s has been updated. Endpoint is %s", ing.ing_name(), ing.ing_route())
            # process_update(ing)
        elif t == "ADDED":
            logging.warning("ingress %s has been created. Endpoint is %s", ing.ing_name(), ing.ing_route())
            # process_add(ing)
            try:
                res = aws.create_resource(restApiId=apiid, parentId=rootid, pathPart=ing.ing_name())
                resid = res['id']
                res = aws.put_method(restApiId=apiid, resourceId=resid, httpMethod='POST', authorizationType='NONE')
                uri = 'http://' + ing.ing_route()
                aws.put_integration(restApiId=apiid, resourceId=resid, httpMethod='POST', type='HTTP', integrationHttpMethod='POST', uri=uri)
            except:
                pass
        else:
            logging.error("Unrecognized type: %s", t)

    resource_version = ""
    while True:
        stream = watch.Watch().stream(ext_beta1.list_ingress_for_all_namespaces,
                                      resource_version=resource_version)
        for event in stream:
            try:
                t = event["type"]
                obj = event["object"]
                ing = Ingress(obj)
                process_meta(t, ing, apiid, rootid)

                # Configure where to resume streaming.
                metadata = obj.metadata
                if metadata:
                    resource_version = metadata.resource_version
            except:
                logging.exception("Error handling event")

if __name__ == "__main__":
    sys.exit(main())
