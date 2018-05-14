# MQTT trigger controller

## Start mqtt in k8s

```
kubectl run mqtt --image=toke/mosquito
kubectl expose deployments mqtt --port 1883
```

## Launch mqtt trigger controller

Create the CRD:

```
kubectl create -f mqtt-triggers.yaml
```

The YAML contains:

```
apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: mqtttriggers.kubeless.io
spec:
  group: kubeless.io
  names:
    kind: MqttTrigger
    listKind: MqttTriggerList
    plural: mqtttriggers
    singular: mqtttrigger
  scope: Namespaced
  version: v1beta1
```

```
kubectl run mqtt-controller --image=
```

## Create event to function binding and test

Create the event to function mapping object. Check the mapping:

```
apiVersion: kubeless.io/v1beta1
kind: MqttTrigger
metadata:
  name: foo
spec:
  functionSelector:
    matchLabels:
      created-by: kubeless
      function: foo
  topic: kubeless
```

POST it to the k8s API server.

```
kubectl create -f mqtt-example.yaml
```

Start sending messages

```
cd ./tests
python ./mpub.py
```

Create a function and check its logs

```
kubeless function deploy foo --runtime python2.7 --from-file foo.py --handler foo.hello
kubectl get pods
kubectl logs -f <pod_name>
```

You should see the MQTT messages being POSTed to the function
