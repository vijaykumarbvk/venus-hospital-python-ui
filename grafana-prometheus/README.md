# Prometheus & Grafana — Venus Hospital

Installs the `kube-prometheus-stack` Helm chart (Prometheus, Alertmanager,
Grafana, node-exporter, kube-state-metrics) into a `prometheus` namespace.

## Install

```bash
# Helm (skip if the bastion user_data already installed it)
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace prometheus

helm install stable prometheus-community/kube-prometheus-stack -n prometheus
```

## Expose the UIs

```bash
# Grafana via an AWS load balancer
kubectl patch svc stable-grafana -n prometheus \
  -p '{"spec":{"type":"LoadBalancer"}}'

# Prometheus via NodePort (keep it off the public internet)
kubectl patch svc stable-kube-prometheus-sta-prometheus -n prometheus \
  -p '{"spec":{"type":"NodePort"}}'

kubectl get svc -n prometheus
```

## Grafana login

```bash
# Username: admin
kubectl get secret -n prometheus stable-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d ; echo
```

## Verify

```bash
kubectl get pods -n prometheus
kubectl get svc  -n prometheus
```

## Dashboards worth importing

In Grafana → Dashboards → Import, paste these IDs:

| ID    | Dashboard                        | What it tells you about Venus |
|-------|----------------------------------|-------------------------------|
| 315   | Kubernetes cluster monitoring    | Node CPU/memory headroom — catch the Kafka pod starving workers |
| 6417  | Kubernetes pods                  | Per-pod restarts; the fastest way to spot a crash-looping service |
| 1860  | Node Exporter Full               | Disk pressure on the EBS volumes backing Kafka and Elasticsearch |

## What is NOT scraped yet

The Flask services expose `/actuator/health` but no Prometheus metrics
endpoint. Prometheus therefore shows you infrastructure health (pods,
nodes, restarts) but not application metrics like request latency or
appointment-booking rates.

To add app metrics, install `prometheus-flask-exporter` in each service:

```python
# in each service's create_app()
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)   # exposes /metrics
```

Then add a `ServiceMonitor` so Prometheus discovers the pods:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: venus-services
  namespace: prometheus
  labels:
    release: stable          # must match the Helm release name
spec:
  namespaceSelector:
    matchNames: ["venus"]
  selector:
    matchLabels:
      tier: backend          # every backend Service carries this label
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```
