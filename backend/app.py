from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from k8s_client import KubernetesClient
from llm_helper import LLMHelper
import logging
from pydantic import BaseModel

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

k8s = KubernetesClient()
llm_helper = LLMHelper()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentCreate(BaseModel):
    name: str
    image: str
    replicas: int = 1
    namespace: str = "default"

class JobCreate(BaseModel):
    name: str
    image: str
    command: list[str] = ["echo", "hello world"]
    namespace: str = "default"

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/deployments")
def list_deployments(namespace: str = "default"):
    try:
        deployments = k8s.apps_v1.list_namespaced_deployment(namespace)
        return [deployment.metadata.name for deployment in deployments.items]
    except Exception as e:
        logger.error(f"Error listing deployments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deployments")
def create_deployment(deployment: DeploymentCreate):
    try:
        k8s.create_deployment(
            name=deployment.name,
            image=deployment.image,
            replicas=deployment.replicas,
            namespace=deployment.namespace
        )
        return {"status": "created", "name": deployment.name}
    except Exception as e:
        logger.error(f"Error creating deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/deployments/{name}")
def delete_deployment(name: str, namespace: str = "default"):
    try:
        k8s.delete_deployment(name, namespace)
        return {"status": "deleted", "name": name}
    except Exception as e:
        logger.error(f"Error deleting deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pods")
def list_pods(namespace: str = "default", label_selector: str = None):
    try:
        pods = k8s.list_pods(namespace, label_selector)
        return [{
            "name": pod.metadata.name,
            "status": pod.status.phase,
            "ip": pod.status.pod_ip
        } for pod in pods.items]
    except Exception as e:
        logger.error(f"Error listing pods: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pods/{name}/logs")
def get_pod_logs(name: str, namespace: str = "default", tail_lines: int = 10):
    try:
        logs = k8s.get_pod_logs(name, namespace, tail_lines)
        return {"logs": logs}
    except Exception as e:
        logger.error(f"Error getting pod logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pods/{name}/logs/summary")
def get_pod_logs_summary(name: str, namespace: str = "default", tail_lines: int = 50, max_tokens: int = 500):
    try:
        # Get the logs first
        logs = k8s.get_pod_logs(name, namespace, tail_lines)
        
        if not logs:
            return {"summary": "No logs available for summarization", "original_logs": ""}
        
        # Generate summary using LLM
        summary = llm_helper.generate_summary(logs, max_tokens)
        
        return {"summary": summary, "original_logs": logs}
            
    except Exception as e:
        logger.error(f"Error getting pod logs summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs")
def create_job(job: JobCreate):
    try:
        k8s.create_job(
            name=job.name,
            image=job.image,
            command=job.command,
            namespace=job.namespace
        )
        return {"status": "created", "name": job.name}
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)