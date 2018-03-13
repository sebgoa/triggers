
# Autoscaling with custom metrics

Since k8s 1.9 on GKE, you can use a [HPA with custom metrics](https://cloud.google.com/kubernetes-engine/docs/tutorials/custom-metrics-autoscaling)

You might want to add your user to the cluster-admin role

## Deploy the custom metrics adapter

```
kubectl create -f https://raw.githubusercontent.com/GoogleCloudPlatform/k8s-stackdriver/master/custom-metrics-stackdriver-adapter/adapter-beta.yaml
```
publish metrics by exposing them in prometheus format and adding a sidecar to do prometheus to stack driver 

export prometheus metrics to stack driver using the sidecar with a deployment like so:

https://github.com/GoogleCloudPlatform/k8s-stackdriver/blob/master/custom-metrics-stackdriver-adapter/examples/prometheus-to-sd/custom-metrics-prometheus-sd.yaml


## explore metrics

check: https://cloud.google.com/kubernetes-engine/docs/how-to/monitoring#metrics_explorer


