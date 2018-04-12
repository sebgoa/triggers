from kubernetes import client, config, watch
import json
import pydoc

GROUP = "yoyo.com"
VERSION = "v1beta1"
PLURAL = "foobars"

PYDOC_RETURN_LABEL = ":return:"

# Removing this suffix from return type name should give us event's object
# type. e.g., if list_namespaces() returns "NamespaceList" type,
# then list_namespaces(watch=true) returns a stream of events with objects
# of type "Namespace". In case this assumption is not true, user should
# provide return_type to Watch class's __init__.
TYPE_LIST_SUFFIX = "List"

config.load_kube_config()

crds = client.CustomObjectsApi()
        
resource_version = ""

class SimpleNamespace:

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _find_return_type(func):
    for line in pydoc.getdoc(func).splitlines():
        if line.startswith(PYDOC_RETURN_LABEL):
            return line[len(PYDOC_RETURN_LABEL):].strip()
    return ""


def iter_resp_lines(resp):
    prev = ""
    for seg in resp.read_chunked(decode_content=False):
        if isinstance(seg, bytes):
            seg = seg.decode('utf8')
        seg = prev + seg
        lines = seg.split("\n")
        if not seg.endswith("\n"):
            prev = lines[-1]
            lines = lines[:-1]
        else:
            prev = ""
        for line in lines:
            if line:
                yield line

class Watcha(object):

    def __init__(self, return_type=None):
        self._raw_return_type = return_type
        self._stop = False
        self._api_client = client.ApiClient()
        self.resource_version = 0

    def stop(self):
        self._stop = True

    def get_return_type(self, func):
        if self._raw_return_type:
            return self._raw_return_type
        return_type = _find_return_type(func)
        if return_type.endswith(TYPE_LIST_SUFFIX):
            return return_type[:-len(TYPE_LIST_SUFFIX)]
        return return_type

    def unmarshal_event(self, data, return_type):
        js = json.loads(data)
        js['raw_object'] = js['object']
        if return_type:
            obj = SimpleNamespace(data=json.dumps(js['raw_object']))
            js['object'] = self._api_client.deserialize(obj, return_type)
            if hasattr(js['object'], 'metadata'):
                self.resource_version = js['object'].metadata.resource_version
        #else:
        #    self.resource_version = js['raw_object']['metadata']['resourceVersion']
        return js

    def stream(self, func, *args, **kwargs):

        self._stop = False
        return_type = self.get_return_type(func)
        kwargs['watch'] = True
        kwargs['_preload_content'] = False

        resp = func(*args, **kwargs)
        try:
            for line in iter_resp_lines(resp):
                yield self.unmarshal_event(line, return_type)
                if self._stop:
                    break
        finally:
            print "hoho"
            kwargs['resource_version'] = self.resource_version
            resp.close()
            resp.release_conn()

while True:

    print "initializing stream"
    stream = Watcha().stream(crds.list_cluster_custom_object,
                                  GROUP, VERSION, PLURAL,
                                  resource_version=resource_version)
    
    for event in stream:
        print event["type"]
        print event["object"]
        print resource_version
        resource_version = crds.list_cluster_custom_object(GROUP, VERSION, PLURAL)["metadata"]["resourceVersion"]