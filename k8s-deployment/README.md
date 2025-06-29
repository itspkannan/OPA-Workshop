# RestAPI OPA Integration - K8s Deployment

This project is an extension of [Project1: Rest API Authz OPA Integration](../restapi-auth-opa-integration/README.md) to deploy on a Kubernetes cluster with OPA as sidecar and policy deployed in AWS S3 ( locally using localstack S3).


## 🧭 Architecture Overview

![alt text](architecture.png)

The system is designed with the following components:

1. **Ingress Controller:**
   Handles incoming API calls from external clients and routes them to services inside the Kubernetes cluster.

2. **Kubernetes (EKS):**
   The core infrastructure where the application and OPA services are deployed. Locally `k3d` is used to create K8s cluster.

3. **Application Service (Pod):**
   A RESTful microservice running in a Pod that handles business logic and external API calls. Before accessing any sensitive resources, it enforces authorization policies.

4. **Open Policy Agent (OPA):**
   Embedded as a sidecar or standalone service, OPA evaluates incoming requests based on defined Rego policies. The application queries OPA to determine whether an action is allowed.

5. **AWS S3**
   The application accesses S3 for storage operations **only after** authorization is granted by OPA. The pod can be configured using [pod level IAM](https://medium.com/kotaicode/aws-iam-roles-for-kubernetes-pods-in-eks-5fdbb2df4ed0) which enabled access to AWS s3 resources. In production, this points to actual AWS S3. Locally, we use LocalStack to simulate AWS services.

6. **Private Network:**
   All components (Ingress, App, OPA) communicate internally within a secure, private network.


## 🧪 Local Development

For local testing and development:

* **K3d** is used to simulate the Kubernetes environment (as a lightweight alternative to EKS).
* **LocalStack** emulates AWS services like S3 so that real cloud access is not needed.

> This enables fully local, policy-driven development and testing with OPA + S3 access patterns.



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
  deploy.view     View  pods, svc, deployment
  describe.cluster Describe the k3d cluster
  events          Show recent warning events
  get.nodes       List Kubernetes nodes
  init.cluster    Initialize the cluster
  pod.describe    Describe pod to view more details
  pod.list        List all pods with labels
  pod.logs        Fetch logs from the pod
  release.status  Show Helm release status
  start.localstack Start localstack service for S3
  start.registry  Start Docker registry using Compose
  stop.registry   Stop Docker registry
  svc.list        List all services in the namespace
  test            Perform test of the deployment
  test.deployment Test if application is deployed
  test.rego.integration Test an OPA auhtorized API endpoint
  undeploy.microservice Uninstall microservice

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
 ✔ Container custom-registry  Started        0.1s
[INFO]  Registry for docker images - Started .
[INFO] K3d Cluster microservice-opa-integration - Creation started.
INFO[0000] Using config file k3d-config.yaml (k3d.io/v1alpha5#simple)
INFO[0000] portmapping '8080:80' targets the loadbalancer: defaulting to [servers:*:proxy agents:*:proxy]
INFO[0000] Prep: Network
INFO[0000] Re-using existing network 'k3d-microservice-opa-integration' (86809379d07e58070642950e9552bf5fd3e7924f3b74e8e2aa04005f3c05d4b3)
INFO[0000] Created image volume k3d-microservice-opa-integration-images
INFO[0000] Starting new tools node...
INFO[0000] Starting node 'k3d-microservice-opa-integration-tools'
INFO[0001] Creating node 'k3d-microservice-opa-integration-server-0'
INFO[0001] Creating node 'k3d-microservice-opa-integration-agent-0'
INFO[0001] Creating node 'k3d-microservice-opa-integration-agent-1'
INFO[0001] Creating LoadBalancer 'k3d-microservice-opa-integration-serverlb'
INFO[0001] Using the k3d-tools node to gather environment information
INFO[0001] Starting new tools node...
INFO[0001] Starting node 'k3d-microservice-opa-integration-tools'
INFO[0002] Starting cluster 'microservice-opa-integration'
INFO[0002] Starting servers...
INFO[0002] Starting node 'k3d-microservice-opa-integration-server-0'
INFO[0004] Starting agents...
INFO[0004] Starting node 'k3d-microservice-opa-integration-agent-1'
INFO[0004] Starting node 'k3d-microservice-opa-integration-agent-0'
INFO[0014] Starting helpers...
INFO[0014] Starting node 'k3d-microservice-opa-integration-serverlb'
INFO[0020] Injecting records for hostAliases (incl. host.k3d.internal) and for 6 network members into CoreDNS configmap...
INFO[0022] Cluster 'microservice-opa-integration' created successfully!
INFO[0022] You can now use it like this:
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

```bash

❯ helm list -n restapi-opa
NAME       	NAMESPACE  	REVISION	UPDATED                             	STATUS  	CHART            	APP VERSION
restapi-opa	restapi-opa	1       	2025-06-28 09:02:53.614026 -0700 PDT	deployed	restapi-opa-0.1.0	0.1.0
```

```bash
❯ helm status restapi-opa -n restapi-opa

NAME: restapi-opa
LAST DEPLOYED: Sat Jun 28 09:02:53 2025
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
NAME                          DATA   AGE
configmap/kube-root-ca.crt    1      13s
configmap/opa-policy-config   1      13s

NAME                              READY   STATUS    RESTARTS   AGE
pod/restapi-opa-7576d4599-w6rf6   2/2     Running   0          13s

NAME                  TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)    AGE
service/restapi-opa   ClusterIP   10.43.19.15   <none>        8080/TCP   13s

NAME                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/restapi-opa   1/1     1            1           13s

NAME                                    DESIRED   CURRENT   READY   AGE
replicaset.apps/restapi-opa-7576d4599   1         1         1       13s

```

8. **Analyze the logs**

```bash
❯ make pod.logs
📜 Logs for pod: restapi-opa-7bb4bb54f6-v85cd
Main  2025-06-28 20:03:10 +0000 INFO: Sanic v24.12.0
Main  2025-06-28 20:03:10 +0000 INFO: Goin' Fast @ http://0.0.0.0:8080
Main  2025-06-28 20:03:10 +0000 INFO: app: OPAWithSanic
Main  2025-06-28 20:03:10 +0000 INFO: mode: production, w/ 2 workers
Main  2025-06-28 20:03:10 +0000 INFO: server: sanic, HTTP/1.1
Main  2025-06-28 20:03:10 +0000 INFO: python: 3.12.11
Main  2025-06-28 20:03:10 +0000 INFO: platform: Linux-6.10.14-linuxkit-aarch64-with-glibc2.36
Main  2025-06-28 20:03:10 +0000 INFO: packages: sanic-routing==23.12.0, sanic-ext==24.12.0
Srv 1 2025-06-28 20:03:10 +0000 INFO: Starting worker [17]
Srv 0 2025-06-28 20:03:10 +0000 INFO: Starting worker [16]
{"addrs":["0.0.0.0:8181"],"diagnostic-addrs":[],"level":"info","msg":"Initializing server.","time":"2025-06-28T20:03:10Z"}
{"level":"debug","msg":"Failed to determine uid/gid of process owner","time":"2025-06-28T20:03:10Z"}
{"level":"debug","msg":"maxprocs: Leaving GOMAXPROCS=12: CPU quota undefined","time":"2025-06-28T20:03:10Z"}
{"level":"info","msg":"Starting bundle loader.","name":"authz","plugin":"bundle","time":"2025-06-28T20:03:10Z"}
{"level":"info","msg":"Starting decision logger.","plugin":"decision_logs","time":"2025-06-28T20:03:10Z"}
{"level":"debug","msg":"Download starting.","time":"2025-06-28T20:03:10Z"}
{"headers":{"Prefer":["modes=snapshot,delta"],"User-Agent":["Open Policy Agent/1.5.1 (linux, amd64)"]},"level":"debug","method":"GET","msg":"Sending request.","time":"2025-06-28T20:03:10Z","url":"http://aws-mock-service:4566/simple-app/authz/bundle.tar.gz"}
{"level":"debug","msg":"Server initialized.","time":"2025-06-28T20:03:10Z"}
{"headers":{"Content-Type":["application/json"],"User-Agent":["Open Policy Agent/1.5.1 (linux, amd64)"]},"level":"debug","method":"POST","msg":"Sending request.","time":"2025-06-28T20:03:10Z","url":"https://telemetry.openpolicyagent.org/v1/version"}
{"headers":{"Accept-Ranges":["bytes"],"Content-Length":["693"],"Content-Type":["application/gzip"],"Date":["Sat, 28 Jun 2025 20:03:10 GMT"],"Etag":["\"1f800cc58fc5073f6b4b3aa5ce4459a3\""],"Last-Modified":["Sat, 28 Jun 2025 20:02:53 GMT"],"Server":["TwistedWeb/24.3.0"],"X-Amz-Id-2":["s9lzHYrFp76ZVxRcpX9+5cjAnEH2ROuNkd2BHfIa6UkFVdtjf5mKR3/eTPFvsiP/XV/VLi31234="],"X-Amz-Request-Id":["1477eab9-b099-4016-b036-c1fc36522371"],"X-Amz-Server-Side-Encryption":["AES256"]},"level":"debug","method":"GET","msg":"Received response.","status":"200 OK","time":"2025-06-28T20:03:10Z","url":"http://aws-mock-service:4566/simple-app/authz/bundle.tar.gz"}
{"level":"debug","msg":"Download in progress.","time":"2025-06-28T20:03:10Z"}
{"level":"debug","msg":"Bundle activation in progress (). Opening storage transaction.","name":"authz","plugin":"bundle","time":"2025-06-28T20:03:10Z"}
{"level":"debug","msg":"Opened storage transaction (4).","name":"authz","plugin":"bundle","time":"2025-06-28T20:03:10Z"}
{"level":"debug","msg":"Closing storage transaction (4).","name":"authz","plugin":"bundle","time":"2025-06-28T20:03:10Z"}
{"level":"info","msg":"Bundle loaded and activated successfully. Etag updated to \"1f800cc58fc5073f6b4b3aa5ce4459a3\".","name":"authz","plugin":"bundle","time":"2025-06-28T20:03:10Z"}
{"level":"debug","msg":"Waiting 8m55.606623331s before next download/retry.","time":"2025-06-28T20:03:10Z"}
{"headers":{"Content-Length":["213"],"Content-Type":["application/json"],"Date":["Sat, 28 Jun 2025 20:03:10 GMT"]},"level":"debug","method":"POST","msg":"Received response.","status":"200 OK","time":"2025-06-28T20:03:10Z","url":"https://telemetry.openpolicyagent.org/v1/version"}
{"current_version":"1.5.1","level":"debug","msg":"OPA is up to date.","time":"2025-06-28T20:03:10Z"}
{"client_addr":"10.42.3.1:41614","level":"info","msg":"Received request.","req_body":"","req_id":1,"req_method":"GET","req_params":{},"req_path":"/health","time":"2025-06-28T20:03:19Z"}
{"client_addr":"10.42.3.1:41614","level":"info","msg":"Sent response.","req_id":1,"req_method":"GET","req_path":"/health","resp_body":"{}\n","resp_bytes":3,"resp_duration":17.00075,"resp_status":200,"time":"2025-06-28T20:03:19Z"}
{"client_addr":"10.42.3.1:53758","level":"info","msg":"Received request.","req_body":"","req_id":2,"req_method":"GET","req_params":{},"req_path":"/health","time":"2025-06-28T20:03:19Z"}
{"client_addr":"10.42.3.1:53758","level":"info","msg":"Sent response.","req_id":2,"req_method":"GET","req_path":"/health","resp_body":"{}\n","resp_bytes":3,"resp_duration":0.48325,"resp_status":200,"time":"2025-06-28T20:03:19Z"}

```

10. **Test the API** 

- Health Check

```bash
❯ curl --fail http://127.0.0.1:30080/health || echo "Server not reachable"

{"status":"ok"}
```

- Invoke protected API resource `/api/v1/users` 

```bash
❯ make test.opa.integration
[INFO] Started integration test of RESTAPI and OPA Integration
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.

[notice] A new release of pip is available: 25.0.1 -> 25.1.1
[notice] To update, run: pip install --upgrade pip
Base64 Encoded Secret: c2VjcmV0MTIz
🔐 Generated JWT Token: eyJhbGciOiJIUzI1NiIsImtpZCI6InNhbXBsZS1hcHAiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJwa2kuZXhhbXBsZS5jb20iLCJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkphbmUgRG9lIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzUxMTQ5NDMzfQ.bnskE69ni-Je083do7O7BK4Kdn2obEnRhvXlh78ZhuM

✅ Sending request to your API service...host.docker.internal:30080
send: b'GET /api/v1/users HTTP/1.1\r\nHost: host.docker.internal:30080\r\nAccept-Encoding: identity\r\nAuthorization: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InNhbXBsZS1hcHAiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJwa2kuZXhhbXBsZS5jb20iLCJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkphbmUgRG9lIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzUxMTQ5NDMzfQ.bnskE69ni-Je083do7O7BK4Kdn2obEnRhvXlh78ZhuM\r\n\r\n'
reply: 'HTTP/1.1 200 OK\r\n'
header: content-length: 67
header: connection: keep-alive
header: content-type: application/json
📥 API Response:
Status: 200
Body: [{"id":"88de0524-b3c2-4c98-ab66-9ed447ffb6fa","name":"John Smith"}]
[INFO] Completed integration n test of RESTAPI and OPA Integration

```

Docker desktop dashboard view of resources used.

![alt text](docker_image.png)