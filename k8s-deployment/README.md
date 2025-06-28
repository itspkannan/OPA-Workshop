# RestAPI OPA Integration - K8s Deployment

This project is an extension of [Project1: Rest API Authz OPA Integration](../restapi-auth-opa-integration/README.md) to deploy on a Kubernetes cluster with OPA as sidecar and policy deployed in AWS S3 ( locally using localstack S3).

## Project

### Structure

```bash
.
├── Makefile
├── README.md
├── docker-compose.yaml
└── k3d-config.yaml

```

The files in the project  are just for creation of K8s cluster , using custom registry for Python RestAPI microservices with Helm charts used for deployment.


### Usage


```bash
❯ make help

Available commands:
  build           Build Python and Rego policies
  build.push      Build, push nginx image
  create.cluster  Create K3d cluster with custom registry
  create.network  Create a K3d network
  delete.cluster  Cleanup resource created during the session.
  delete.cluster  Delete the k3d cluster
  delete.network  Delete a K3d network
  deploy.microservice Deploy microservice
  deploy.rego     Deploy the policy to S3 bucket
  describe.cluster Describe the k3d cluster
  get.nodes       List Kubernetes nodes
  init.cluster    Initialize the cluster
  start.localstack Start localstack service for S3
  start.registry  Start Docker registry using Compose
  stop.registry   Stop Docker registry
  test            Perform test of the deployment
  test.deployment Test if application is deployed
  test.rego.integration Test an OPA auhtorized API endpoint

```

## Create Helm Charts for Deployment

```bash

helm create restapi-opa
```

- Edit all yaml files to include in metadata.
  
```yaml
  namespace: {{ .Values.namespace }}
```

- In `values.yaml` add the value for namespace.
  
```yaml
namespace: restapi-opa
```

- Added the below opa config for sidecard configuration in `rest-api/files` helm chart folder.
  
```yaml
services:
  - name: authz_policies
    url: http://aws-mock-service:4566
    credentials:
      type: aws
      aws:
        region: us-west-1
        access_key_id: test
        secret_access_key: test

bundles:
  authz:
    service: authz_policies
    resource: /simple-app/authz/bundle.tar.gz
    polling:
      min_delay_seconds: 300
      max_delay_seconds: 600

decision_logs:
  console: true
  level: debug
  formatting:
    json: true

```

-  Added `opa-configmap.yaml` file

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: opa-policy-config
  namespace: {{ .Values.namespace }}
data:
  authz_config.yaml: |
{{ .Files.Get "files/authz_config.yaml" | indent 4 }}

```

-  Update `restapi-opa/templates/deployment.yaml` to include OPA sidecar.

```yaml
      containers:
        - name: {{ .Chart.Name }}
          ....
          ....
        - name: opa
          image: openpolicyagent/opa:latest
          args:
            - "run"
            - "--server"
            - "--config-file=/config/authz_config.yaml"
          ports:
            - containerPort: 8181
              name: opa
          volumeMounts:
            - mountPath: /config
              name: opa-policy
            - mountPath: /policies
              name: opa-policy

      volumes:
        {{- if .Values.volumes }}
        {{- toYaml .Values.volumes | nindent 8 }}
        {{- end }}
        - name: opa-policy
          configMap:
            name: opa-policy

```

- Validate using helm dry-run

```bash
helm install restapi-opa restapi-opa --namespace restapi-opa --dry-run --debug
```


## Deployment and Testing 

1.  **Start docker registry, create K3d cluster**

```bash
❯ make init.cluster
[INFO] Creating docker network k3d-microservice-opa-integration.
docker network create k3d-microservice-opa-integration || true
f05942aa88232626b88a66f387d1b166d87c30927b15ba9186b6e3a399c42ae6
[INFO] Registry for docker images - Starting.
[+] Running 1/1
 ✔ Container custom-registry  Started                                                                                                                                                                                                           0.1s
[INFO]  Registry for docker images - Started .
[INFO] K3d Cluster microservice-opa-integration - Creation started.
INFO[0000] Using config file k3d-config.yaml (k3d.io/v1alpha5#simple)
INFO[0000] portmapping '8080:80' targets the loadbalancer: defaulting to [servers:*:proxy agents:*:proxy]
INFO[0000] Prep: Network
INFO[0000] Created network 'k3d-custom-registry-cluster'
INFO[0000] Created image volume k3d-custom-registry-cluster-images
INFO[0000] Starting new tools node...
INFO[0000] Starting node 'k3d-custom-registry-cluster-tools'
INFO[0001] Creating node 'k3d-custom-registry-cluster-server-0'
INFO[0001] Creating node 'k3d-custom-registry-cluster-agent-0'
INFO[0001] Creating node 'k3d-custom-registry-cluster-agent-1'
INFO[0001] Creating LoadBalancer 'k3d-custom-registry-cluster-serverlb'
INFO[0001] Using the k3d-tools node to gather environment information
INFO[0001] Starting new tools node...
INFO[0001] Starting node 'k3d-custom-registry-cluster-tools'
INFO[0002] Starting cluster 'custom-registry-cluster'
INFO[0002] Starting servers...
INFO[0002] Starting node 'k3d-custom-registry-cluster-server-0'
INFO[0004] Starting agents...
INFO[0004] Starting node 'k3d-custom-registry-cluster-agent-1'
INFO[0004] Starting node 'k3d-custom-registry-cluster-agent-0'
INFO[0016] Starting helpers...
INFO[0016] Starting node 'k3d-custom-registry-cluster-serverlb'
INFO[0022] Injecting records for hostAliases (incl. host.k3d.internal) and for 5 network members into CoreDNS configmap...
INFO[0024] Cluster 'custom-registry-cluster' created successfully!
INFO[0024] You can now use it like this:
kubectl cluster-info
[INFO] K3d Cluster microservice-opa-integration - Creation Completed.
```

2. **Build and Push image to registry**

```bash
❯ make build build.push
cd "../restapi-auth-opa-integration" && make  build
Building restapi-auth-opa-integration (0.1.0)
Building sdist
  - Building sdist
  - Built restapi_auth_opa_integration-0.1.0.tar.gz
Building wheel
  - Building wheel
  - Built restapi_auth_opa_integration-0.1.0-py3-none-any.whl
WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested
[+] Building 0.8s (15/15) FINISHED                                                                                                                                                                                              docker:desktop-linux
 => [internal] load build definition from dockerfile                                                                                                                                                                                            0.0s
 => => transferring dockerfile: 2.12kB                                                                                                                                                                                                          0.0s
 => [internal] load metadata for docker.io/library/python:3.12-slim-bookworm                                                                                                                                                                    0.7s
 => [internal] load .dockerignore                                                                                                                                                                                                               0.0s
 => => transferring context: 640B                                                                                                                                                                                                               0.0s
 => [python-base 1/2] FROM docker.io/library/python:3.12-slim-bookworm@sha256:e55523f127124e5edc03ba201e3dbbc85172a2ec40d8651ac752364b23dfd733                                                                                                  0.0s
 => [internal] load build context                                                                                                                                                                                                               0.0s
 => => transferring context: 5.82kB                                                                                                                                                                                                             0.0s
 => CACHED [python-base 2/2] RUN  apt-get update -q &&     apt-get install -y --no-install-recommends -y locales &&     apt-get remove -y ncurses-base --allow-remove-essential &&     localedef -i en_US -c -f UTF-8 -A /usr/share/locale/loc  0.0s
 => CACHED [app-builder 1/3] WORKDIR /app                                                                                                                                                                                                       0.0s
 => CACHED [app-builder 2/3] COPY pyproject.toml poetry.lock ./                                                                                                                                                                                 0.0s
 => CACHED [app-builder 3/3] RUN pip3 --disable-pip-version-check install --no-cache-dir --upgrade "pip==25.1" "setuptools==80.0.0" &&     pip3 --disable-pip-version-check install --no-cache-dir "poetry==2.1.1"  &&     poetry config virtu  0.0s
 => CACHED [production 2/6] COPY --from=app-builder /app/.venv /app/.venv/                                                                                                                                                                      0.0s
 => CACHED [production 3/6] COPY main.py /app                                                                                                                                                                                                   0.0s
 => CACHED [production 4/6] COPY src/main/python/restapi_auth_opa_integration /app/restapi_auth_opa_integration                                                                                                                                 0.0s
 => CACHED [production 5/6] COPY deployment/app/config /app/config                                                                                                                                                                              0.0s
 => CACHED [production 6/6] RUN groupadd -r restapi_opa --gid=10000 &&     useradd --no-create-home -s /bin/false -r -g restapi_opa --uid=999 restapi_opa &&     id -u restapi_opa | xargs -I{} chown -R {}:{} /app                             0.0s
 => exporting to image                                                                                                                                                                                                                          0.0s
 => => exporting layers                                                                                                                                                                                                                         0.0s
 => => writing image sha256:6b3a6823d318622e256d813ba64c41a531949cb22c678654f46952511f888504                                                                                                                                                    0.0s
 => => naming to docker.io/library/restapi-auth-opa-integration-microservice:latest                                                                                                                                                             0.0s

 1 warning found (use docker --debug to expand):
 - UndefinedVar: Usage of undefined variable '$PYTHONPATH' (line 50)

What's next:
    View a summary of image vulnerabilities and recommendations → docker scout quickview
docker tag "restapi-auth-opa-integration-microservice:latest" localhost:5000/"restapi-auth-opa-integration-microservice:latest"
docker push localhost:5000/"restapi-auth-opa-integration-microservice:latest"
The push refers to repository [localhost:5000/restapi-auth-opa-integration-microservice]
f1fac5ccc86b: Pushed
d2281abe240e: Pushed
68a264ca3cae: Pushed
e9b0530a878e: Pushed
b99575ae5caa: Pushed
56e6859a5d44: Pushed
f9bc7484b5ba: Pushed
39180fa1de84: Pushed
b14c937a5866: Pushed
6128ef32a45e: Pushed
6edfb9bfff29: Pushed
latest: digest: sha256:492775668ff173c76580c528f00c478f3ff0dd80bf323ea8e48f484cc4a576e9 size: 2623

```

3. **Verify if the registry has your image**

```bash
❯ curl http://localhost:5000/v2/_catalog

{"repositories":["restapi-auth-opa-integration-microservice"]}
```

4. **Start localstack for S3 Service**

```bash
❯ make start.localstack
cd "../restapi-auth-opa-integration" && make  start.localstack

[INFO] Starting localstack Service

[+] Running 1/1
 ✔ Container aws-mock-service  Started
```

5. **Deploy bundle to S3**


```bash
❯ make deploy.rego
cd "../restapi-auth-opa-integration" ; DOCKER_NETWORK=k3d-microservice-opa-integration make  deploy.rego deploy.rego.validate

[INFO] Deploying bundle.tar.gz to S3 Bucket

🪣 Creating bucket ...
make_bucket: simple-app
📦 Uploading bundle.tar.gz to s3://simple-app...
upload: ../authz/bundle.tar.gz to s3://simple-app/authz/bundle.tar.gz

[INFO] Validate deployment of bundle.tar.gz to S3 Bucket

2025-06-28 15:11:16        693 bundle.tar.gz
```

6. **Deploy Microservice **

```bash
❯ helm install restapi-opa restapi-opa --namespace restapi-opa --create-namespace

NAME: restapi-opa
LAST DEPLOYED: Sat Jun 28 08:43:52 2025
NAMESPACE: restapi-opa
STATUS: deployed
REVISION: 1
NOTES:
1. Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods --namespace restapi-opa -l "app.kubernetes.io/name=restapi-opa,app.kubernetes.io/instance=restapi-opa" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(kubectl get pod --namespace restapi-opa $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace restapi-opa port-forward $POD_NAME 8080:$CONTAINER_PORT
```

7. **Display deployed resources**

```bash
❯ make deploy.view
kubectl get configmap,pods,svc,deployment,replicaset,hpa -n restapi-opa
NAME                          DATA   AGE
configmap/kube-root-ca.crt    1      43s
configmap/opa-policy-config   1      43s

NAME                               READY   STATUS         RESTARTS   AGE
pod/restapi-opa-547b6f5b5c-77w4z   1/2     ErrImagePull   0          43s

NAME                  TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
service/restapi-opa   ClusterIP   10.43.61.251   <none>        80/TCP    43s

NAME                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/restapi-opa   0/1     1            0           43s

NAME                                     DESIRED   CURRENT   READY   AGE
replicaset.apps/restapi-opa-547b6f5b5c   1         1         0       43s


```

Docker desktop dashboard view of resources used.

![alt text](docker_image.png)