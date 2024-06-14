from fastapi import FastAPI
from kubernetes import client, config as k8s_config
import os
from prometheus_api_client import PrometheusConnect  
app = FastAPI()

# Load the Kubernetes configuration based on the environment
if 'KUBERNETES_SERVICE_HOST' in os.environ:
    k8s_config.load_incluster_config()
else:
    k8s_config.load_kube_config()

@app.post("/createDeployment/{deployment_name}")
async def create_deployment(deployment_name: str):
    api_instance = client.AppsV1Api()
    
    deployment = client.V1Deployment(
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector={'matchLabels': {'app': deployment_name}},
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={'app': deployment_name}),
                spec=client.V1PodSpec(
                    containers=[client.V1Container(
                        name=deployment_name,
                        image="nginx",
                        ports=[client.V1ContainerPort(container_port=80)]
                    )]
                )
            )
        )
    )
    
    api_instance.create_namespaced_deployment(namespace="default", body=deployment)
    return {"message": f"Deployment {deployment_name} created successfully."}


@app.get("/getPromdetails")
def get_prom_details():
    prom = PrometheusConnect(url="http://192.168.49.2:32705", disable_ssl=True)
    query = 'up'  # example query to get the status of targets
    result = prom.custom_query(query=query)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

