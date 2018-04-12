from kubernetes import client, config, watch

config.load_kube_config()

crds = client.CustomObjectsApi()
v1 = client.CoreV1Api()
        
resource_version = ""

while True:

    stream = watch.Watch().stream(v1.list_namespace,resource_version=resource_version)
    resource_version = v1.list_namespace().metadata.resource_version
    
    for event in stream:
        t = event["type"]
        obj = event["object"]
    
        print t
        
        if event["type"] == 'Error':
            print event["raw_object"]["message"]