from kubernetes import client, config
import crd

GROUP = "yoyo.com"
VERSION = "v1beta1"
PLURAL = "foobars"

config.load_kube_config()

crds = client.CustomObjectsApi()
        
resource_version = ""

while True:

    print "initializing stream"
    stream = crd.Watch().stream(crds.list_cluster_custom_object,
                                  GROUP, VERSION, PLURAL,
                                  resource_version=resource_version)
    
    for event in stream:
        print event["type"]
        print event["object"]
        print resource_version
        resource_version = crds.list_cluster_custom_object(GROUP, VERSION, PLURAL)["metadata"]["resourceVersion"]