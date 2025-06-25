# Kubernetes POC - Cluster Management with AI-Powered Log Analysis

A comprehensive Kubernetes cluster management application with AI-powered log analysis capabilities. This project includes a FastAPI backend for Kubernetes operations and a Streamlit frontend for easy cluster management.

## 🚀 Features

- **Pod Management**: View, create, and delete pods
- **Deployment Management**: Create and manage deployments
- **Job Management**: Create and monitor Kubernetes jobs
- **Log Analysis**: View pod logs with AI-powered summarization
- **Multi-LLM Support**: OpenAI and Ollama integration for log analysis
- **Real-time Monitoring**: Live pod status and health checks

## 📋 Prerequisites

Before running this application, ensure you have the following installed:

- **Docker Desktop** (with Kubernetes enabled)
- **Minikube** (for local Kubernetes cluster)
- **kubectl** (Kubernetes command-line tool)
- **Python 3.9+** (for local development)

### Installing Prerequisites

#### 1. Install Minikube
```bash
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows
# Download from https://minikube.sigs.k8s.io/docs/start/
```

#### 2. Install kubectl
```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Windows
# Download from https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
```

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd kubernetes_poc
```

### 2. Start Minikube
```bash
minikube start
```

### 3. Configure Environment Variables
```bash
# Copy the environment template
cp env.template .env

# Edit the .env file with your configuration
nano .env
```

**Environment Variables:**
```bash
# LLM Configuration
LLM_TYPE=openai  # or "ollama" for local LLM

# OpenAI Configuration (required when LLM_TYPE=openai)
OPENAI_API_KEY=your_openai_api_key_here

# Ollama Configuration (optional, used when LLM_TYPE=ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### 4. Build and Deploy

#### Option A: Using Docker Compose (for local development)
```bash
# Build and start services
docker-compose up --build

# Access the application
# Frontend: http://localhost:8501
# Backend: http://localhost:8000
```

#### Option B: Using Kubernetes (recommended)
```bash
# Build Docker images in Minikube's Docker environment
eval $(minikube docker-env)

# Build backend image
docker build -t k8s-poc-backend:v2 backend/

# Build frontend image
docker build -t k8s-poc-frontend:latest frontend/

# Deploy to Kubernetes
kubectl apply -f k8s/

# Create ConfigMap from environment variables
kubectl create configmap llm-config --from-env-file=.env

# Apply the updated deployment
kubectl apply -f k8s/backend-deployment.yaml

# Access the application
minikube service frontend
```

### 5. Verify Deployment
```bash
# Check pod status
kubectl get pods

# Check services
kubectl get services

# Check ConfigMap
kubectl get configmap llm-config
```

## 🎯 Usage Guide

### Accessing the Application

1. **Start the application** using one of the methods above
2. **Open your browser** to the provided URL
3. **Navigate through the tabs**:
   - **Deployments**: Create and manage deployments
   - **Pods**: View pod information
   - **Jobs**: Create and monitor jobs
   - **Logs**: View logs and generate AI summaries

### Using AI-Powered Log Analysis

1. **Go to the "Logs" tab**
2. **Enter a pod name** (e.g., `backend-8497d9f466-9sd6v`)
3. **Set the number of log lines** to analyze
4. **Click "Log Summary"** to generate an AI summary
5. **View the summary** and expand to see original logs

### Creating Deployments

1. **Go to the "Deployments" tab**
2. **Fill in the deployment details**:
   - Name: `my-app`
   - Image: `nginx:alpine`
   - Replicas: `2`
   - Namespace: `default`
3. **Click "Create Deployment"**

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Minikube Cluster Issues

**Problem**: `minikube start` fails
```bash
# Solution: Reset Minikube
minikube delete
minikube start --driver=docker
```

**Problem**: Pods stuck in `Pending` status
```bash
# Check node resources
kubectl describe nodes

# Increase Minikube resources
minikube stop
minikube start --cpus=4 --memory=8192 --driver=docker
```

#### 2. Docker Image Issues

**Problem**: `ErrImagePull` errors
```bash
# Ensure you're using Minikube's Docker daemon
eval $(minikube docker-env)

# Rebuild images
docker build -t k8s-poc-backend:v2 backend/
docker build -t k8s-poc-frontend:latest frontend/

# Restart deployments
kubectl rollout restart deployment/backend
kubectl rollout restart deployment/frontend
```

#### 3. Backend Service Issues

**Problem**: Backend pod crashes on startup
```bash
# Check pod logs
kubectl logs <pod-name>

# Common causes:
# - Missing environment variables
# - Invalid API keys
# - Network connectivity issues
```

**Problem**: "LLM not configured" error
```bash
# Verify ConfigMap exists
kubectl get configmap llm-config

# Check environment variables in pod
kubectl exec <pod-name> -- env | grep -E "(LLM_TYPE|OPENAI_API_KEY)"

# Recreate ConfigMap if needed
kubectl delete configmap llm-config
kubectl create configmap llm-config --from-env-file=.env
kubectl rollout restart deployment/backend
```

#### 4. Frontend Service Issues

**Problem**: Frontend not accessible
```bash
# Check service status
kubectl get services

# Check pod logs
kubectl logs <frontend-pod-name>

# Restart frontend service
kubectl rollout restart deployment/frontend
```

#### 5. RBAC Permission Issues

**Problem**: 403 Forbidden errors
```bash
# Apply RBAC configuration
kubectl apply -f k8s/backend-rbac.yaml

# Verify RBAC resources
kubectl get role,rolebinding
```

#### 6. Network Connectivity Issues

**Problem**: Services can't communicate
```bash
# Check if services are running
kubectl get pods -o wide

# Test service connectivity
kubectl exec <pod-name> -- curl http://backend:8000/health

# Check DNS resolution
kubectl exec <pod-name> -- nslookup backend
```

### Debugging Commands

```bash
# Get detailed pod information
kubectl describe pod <pod-name>

# View pod logs
kubectl logs <pod-name>

# Execute commands in pod
kubectl exec -it <pod-name> -- /bin/bash

# Check service endpoints
kubectl get endpoints

# View ConfigMap contents
kubectl get configmap llm-config -o yaml

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Performance Optimization

```bash
# Increase Minikube resources for better performance
minikube stop
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable Minikube addons
minikube addons enable metrics-server
minikube addons enable dashboard
```

## 📁 Project Structure

```
kubernetes_poc/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── k8s_client.py       # Kubernetes client wrapper
│   ├── llm_helper.py       # LLM integration helper
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container
├── frontend/
│   ├── app.py             # Streamlit application
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile        # Frontend container
├── k8s/
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   └── backend-rbac.yaml
├── docker-compose.yaml    # Local development
├── env.template          # Environment template
└── README.md            # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues not covered in this troubleshooting guide:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Include logs and error messages
4. Specify your environment (OS, versions, etc.)

## 🔄 Updates

To update the application:

```bash
# Pull latest changes
git pull origin main

# Rebuild and redeploy
eval $(minikube docker-env)
docker build -t k8s-poc-backend:v2 backend/
docker build -t k8s-poc-frontend:latest frontend/
kubectl rollout restart deployment/backend
kubectl rollout restart deployment/frontend
``` 