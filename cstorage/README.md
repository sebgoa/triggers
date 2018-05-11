Create a topic and a subscription

```
gsutil notification create -t foobar -f json gs://sebgoa
gsutil notification list gs://sebgoa
gcloud pubsub subscriptions create foobarsub --topic foobar
Created subscription [projects/skippbox/subscriptions/foobarsub].
```

Install Python client

```
sudo pip install --upgrade google-cloud-pubsub
```

IAM or scope of instances.

Create the google creds secrets

```
kubectl create secret generic pubsub --from-file=/path/to/key.json
```
