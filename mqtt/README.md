# MQTT trigger controller

## Start mqtt in k8s

```
kubectl run mqtt --image=toke/mosquito
kubectl expose deployments mqtt --port 1883
```

## Launch mqtt trigger controller


## Create event to function binding and test

