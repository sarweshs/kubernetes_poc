from kubernetes import client, config
from kubernetes.client import ApiException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KubernetesClient:
    def __init__(self):
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                config.load_kube_config()
            except config.ConfigException as e:
                raise Exception("Could not configure kubernetes python client")

        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.batch_v1 = client.BatchV1Api()

    def list_pods(self, namespace="default", label_selector=None):
        """List pods in a namespace"""
        try:
            return self.core_v1.list_namespaced_pod(namespace, label_selector=label_selector)
        except ApiException as e:
            logger.error(f"Exception when calling CoreV1Api->list_namespaced_pod: {e}")
            raise

    def get_pod_logs(self, pod_name, namespace="default", tail_lines=10):
        """Get logs from a pod"""
        try:
            return self.core_v1.read_namespaced_pod_log(
                pod_name, namespace, tail_lines=tail_lines
            )
        except ApiException as e:
            logger.error(f"Exception when calling CoreV1Api->read_namespaced_pod_log: {e}")
            raise

    def create_deployment(self, name, image, replicas=1, namespace="default"):
        """Create a deployment"""
        try:
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(name=name),
                spec=client.V1DeploymentSpec(
                    replicas=replicas,
                    selector=client.V1LabelSelector(
                        match_labels={"app": name}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": name}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=name,
                                    image=image
                                )
                            ]
                        )
                    )
                )
            )
            
            return self.apps_v1.create_namespaced_deployment(
                namespace, deployment
            )
        except ApiException as e:
            logger.error(f"Exception when calling AppsV1Api->create_namespaced_deployment: {e}")
            raise

    def delete_deployment(self, name, namespace="default"):
        """Delete a deployment"""
        try:
            return self.apps_v1.delete_namespaced_deployment(
                name, namespace
            )
        except ApiException as e:
            logger.error(f"Exception when calling AppsV1Api->delete_namespaced_deployment: {e}")
            raise

    def create_job(self, name, image, command, namespace="default"):
        """Create a job"""
        try:
            job = client.V1Job(
                metadata=client.V1ObjectMeta(name=name),
                spec=client.V1JobSpec(
                    template=client.V1PodTemplateSpec(
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=name,
                                    image=image,
                                    command=command
                                )
                            ],
                            restart_policy="Never"
                        )
                    )
                )
            )
            
            return self.batch_v1.create_namespaced_job(
                namespace, job
            )
        except ApiException as e:
            logger.error(f"Exception when calling BatchV1Api->create_namespaced_job: {e}")
            raise

    # [Previous methods from the original k8s_client.py remain the same]
    # Add any additional methods you need