import streamlit as st
import requests
import pandas as pd
import time

# Configuration
BACKEND_URL = "http://backend:8000"  # For Docker compose
# BACKEND_URL = "http://localhost:8000"  # For local testing

st.set_page_config(page_title="Kubernetes Manager", layout="wide")

def check_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            return True
    except:
        return False
    return False

if not check_backend():
    st.error("Backend service is not available. Please ensure the FastAPI backend is running.")
    st.stop()

st.title("Kubernetes Cluster Manager")

tab1, tab2, tab3, tab4 = st.tabs(["Deployments", "Pods", "Jobs", "Logs"])

with tab1:
    st.header("Deployments Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create Deployment")
        with st.form("create_deployment"):
            name = st.text_input("Deployment Name", "nginx-deployment")
            image = st.text_input("Container Image", "nginx:alpine")
            replicas = st.number_input("Replicas", min_value=1, value=1)
            namespace = st.text_input("Namespace", "default")
            
            if st.form_submit_button("Create Deployment"):
                data = {
                    "name": name,
                    "image": image,
                    "replicas": replicas,
                    "namespace": namespace
                }
                response = requests.post(f"{BACKEND_URL}/deployments", json=data)
                if response.status_code == 200:
                    st.success(f"Deployment {name} created successfully!")
                else:
                    st.error(f"Error creating deployment: {response.json().get('detail')}")
    
    with col2:
        st.subheader("Existing Deployments")
        if st.button("Refresh Deployments"):
            response = requests.get(f"{BACKEND_URL}/deployments")
            if response.status_code == 200:
                deployments = response.json()
                if deployments:
                    df = pd.DataFrame(deployments, columns=["Name"])
                    st.dataframe(df)
                    
                    selected_deployment = st.selectbox("Select deployment to delete", deployments)
                    if st.button("Delete Deployment"):
                        response = requests.delete(f"{BACKEND_URL}/deployments/{selected_deployment}")
                        if response.status_code == 200:
                            st.success(f"Deployment {selected_deployment} deleted successfully!")
                            time.sleep(1)
                            st.experimental_rerun()
                        else:
                            st.error(f"Error deleting deployment: {response.json().get('detail')}")
                else:
                    st.info("No deployments found")
            else:
                st.error(f"Error fetching deployments: {response.json().get('detail')}")

with tab2:
    st.header("Pod Information")
    namespace = st.text_input("Namespace for Pods", "default")
    
    if st.button("Get Pods"):
        response = requests.get(f"{BACKEND_URL}/pods", params={"namespace": namespace})
        if response.status_code == 200:
            pods = response.json()
            if pods:
                df = pd.DataFrame(pods)
                st.dataframe(df)
            else:
                st.info("No pods found in the namespace")
        else:
            st.error(f"Error fetching pods: {response.json().get('detail')}")

with tab3:
    st.header("Job Management")
    
    st.subheader("Create Job")
    with st.form("create_job"):
        name = st.text_input("Job Name", "test-job")
        image = st.text_input("Job Image", "busybox")
        command = st.text_area("Command (one per line)", "echo\nHello from Job").split("\n")
        namespace = st.text_input("Job Namespace", "default")
        
        if st.form_submit_button("Create Job"):
            data = {
                "name": name,
                "image": image,
                "command": command,
                "namespace": namespace
            }
            response = requests.post(f"{BACKEND_URL}/jobs", json=data)
            if response.status_code == 200:
                st.success(f"Job {name} created successfully!")
            else:
                st.error(f"Error creating job: {response.json().get('detail')}")

with tab4:
    st.header("Pod Logs Viewer")
    
    namespace = st.text_input("Namespace for Logs", "default")
    pod_name = st.text_input("Pod Name")
    tail_lines = st.number_input("Number of lines to fetch", min_value=1, value=50)
    
    if st.button("Get Logs") and pod_name:
        response = requests.get(
            f"{BACKEND_URL}/pods/{pod_name}/logs",
            params={"namespace": namespace, "tail_lines": tail_lines}
        )
        if response.status_code == 200:
            logs = response.json().get("logs", "No logs available")
            st.subheader(f"Logs for {pod_name}")
            st.code(logs)
        else:
            st.error(f"Error fetching logs: {response.json().get('detail')}")