Launch this custom runtime, it will export metrics to stackdriver

Used for testing auto-scaling on GKE using custom metrics

```
kubeless function deploy foobar --runtime-image kubeless/stackdriver --from-file hello.py
```
