
# Configure

Create a bucket `bridgedemo`
Create a notification for bucket events
Create a subscription for the topic used to publish the notifications

```
gsutil notification create -t tmdemo -f json gs://bridgedemo
gsutil notification list gs://bridgedemo
gcloud pubsub subscriptions create bridgedemosub --topic tmdemo
```

# Build

```
docker build -t gcr.io/triggermesh/googlecloudstorage .
```

# Deploy

The source as a deployment and a sink binding

```
kubectl apply -f d.yaml
kubectl apply -f sinkb.yaml
```
