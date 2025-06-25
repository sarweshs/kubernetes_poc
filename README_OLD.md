## Deployment Instructions
# Local Development with Docker Compose
# Build and start the services:
```bash
docker-compose up --build
```

# Kubernetes Deployment
## Build Docker images:
```bash
docker build -t k8s-poc-backend ./backend
docker build -t k8s-poc-frontend ./frontend
```

# Load images into Kubernetes (if using Minikube):
```bash
minikube image load k8s-poc-backend:latest
minikube image load k8s-poc-frontend:latest
```

# Apply Kubernetes manifests:

```bash
kubectl apply -f k8s/
```

# Access the application:
```bash
minikube service frontend
```
