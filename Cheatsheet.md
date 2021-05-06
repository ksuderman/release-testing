# Keith's Cheat Sheet

### Config management

```
kubectl config view                         # list all configuration (clusters, contexts, users, etc.)
kubectl config current-context              # list the current context
kubectl config get-contexts                 # list all contexts
kubectl config use-context docker-desktop   # select a context
kubectl config use-context gke_anvil-and-terra-development_us-east1-b_keith-rel-test-cluster
```

### Common Commands
```
kubectl get pods
kubectl get deployments
kubectl get events
kubectl get services

kubectl descibe pod <pod_id>
kubectl logs <pod_id>
kubectl logs -f <pod_id>

kubectl create deployment hello-node --image=k8s.gcr.io/echoserver:1.4
kubectl expose deployment hello-node --type=LoadBalancer --port=8080
kubectl delete service hello-node
kubectl delete deployment hello-node
```

### Attach to a container
To attach to a container running inside a pod you need the pod id and the name of the container as returned by `kubectl describe pod`

```
kubectl exec -it <pod_id> --container <container_name> -- /bin/bash
```

### Port forwarding

```
kubectl port-forward <pod_id> <8000>:<80>
```
Accessing http://localhost:8000 will now access port 80 in the pod.

## Google Cloud

```
gcloud projects list
```

## Helm

```
helm dependency update
helm dep up

helm repo index /path/to/charts/
helm repo index --url=https://ksuderman.github.io/helm_charts/ /path/to/chart
helm repo add https://ksuderman.github.io/helm_charts/
helm repo list

helm package /path/to/chart
```

