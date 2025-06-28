# Rest API Authorization using OPA

This Python project is a **proof of concept** demonstrating the integration of [Open Policy Agent (OPA)](https://www.openpolicyagent.org/) for **authorization of a REST API**. 

The poc include following approaches of loading `Policies`
1.  Local File System.
2.  Loading from a Remote service( in poc a Python web service is started to serve the Policy).
3.  Loading from AWS S3 bucket (The security is controlled by POD's IAM rules in actual Prod deployment)


## ✨ Features

* 📦 Python 3.11 with [Poetry](https://python-poetry.org/) for dependency and virtualenv management
* 🧹 Code Quality:
  * [Ruff](https://github.com/astral-sh/ruff) for formatting, linting, and import sorting
  * [Hadolint](https://github.com/hadolint/hadolint) for Dockerfile linting
  * [Mypy](http://mypy-lang.org/) for static type checking
* ✅ Testing: [Pytest](https://docs.pytest.org/) with coverage reporting
* 🛠️ Task Automation: `Makefile` with useful development commands
* 🐳 Docker support
* 🔐 Open Policy Agent (OPA) integration for dynamic API authorization

###🚀 Usage

```bash
❯ make help

Available commands:
  bootstrap             Bootstrap environment
  build                 Build Python and Rego policies
  build.docker          Build application docker image
  build.python          Build python source
  build.rego            Build policies into a gzipped file
  clean                 clean all generated files
  clean.python        clean the development environment temporary files
  clean.rego          clean policies build folder
  deploy.rego           Deploy the policy to S3 bucket
  deploy.rego.validate  Validate rego policy deployment to S3
  docker.image.describe View Application docker image view
  format.python         Format code using Ruff (Black-compatible)
  help                  Help message
  infra.clean         clean the infrastructure
  init.infra            Create the infrastructure
  init.python           Initialize the Poetry development environment
  lint                  Run static analysis on Python, Rego and Dockerfile
  lint.dockerfile       Run lint for dockerfile
  lint.python           Run static analysis with Ruff and Mypy
  logs.app              View application logs
  logs.authz            View logs of Authorization Service (Open Policy Agent)
  policy.check          Run OPA check on Policies
  policy.eval           Evaluate the Rego Policies
  runtime.view          view the active docker container
  start                 Start Authorization Services and Application
  start.app             Start App
  start.authz           Start Authorization Service (Open Policy Agent)
  start.localstack      Start localstack service for S3
  stop                  Stop Authorization Services and Application
  stop.app              Stop App
  stop.authz            Stop Authorization Service (Open Policy Agent)
  stop.localstack       Stop localstack service
  test                  Run tests for Rego and Python src code
  test.python           Run tests with Pytest and show coverage
  test.rego             Test the policy against a valid input using JWT token
  test.rego.integration Test the policy against a valid input using JWT token
  token.generate        Generate a mock JWT token 
```

---


## API, Middleware and OPA Integration

The middleware uses the `Authorization` HTTP header to extract a **JWT token**. This token contains the user's role, which is verified and decoded securely using OPA.

1. `Authorization: Bearer <JWT_TOKEN>` is passed with the request
2. Middleware forwards the token, method, and path to OPA
3. OPA decodes and verifies the token
4. Access is allowed or denied based on decoded role

```http
GET /api/v1/users HTTP/1.1
Host: localhost:8080
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 👤 UserController – API Overview

The `UserController` defines a simple CRUD interface for user management. It is responsible for handling the following endpoints:

### Endpoints

| Method | Endpoint      | Description             | Role Check    |
| ------ | ------------- | ----------------------- |---------------|
| GET    | `/users`      | Fetch all users         | Admin         |
| POST   | `/users`      | Create a new user       | Admin         |
| PUT    | `/users/<id>` | Update an existing user | Admin or User |
| DELETE | `/users/<id>` | Delete a user           | Admin         |

All endpoints in the `UserController` are protected by **OPA policies**. Each request is authorized using a custom Sanic middleware that queries the OPA engine to evaluate access based on:

* `x-role` header from the request
* HTTP method (GET, POST, etc.)
* Endpoint path (`request.path`)

### OPA Integration

This project supports **three modes** for running the Open Policy Agent (OPA) Authorization Service:

The policies are split into reusable packages:

* `common.jwt_utils`: Responsible for decoding and verifying JWTs
* `simple.authz`: Implements authorization rules using decoded claims

```
deployment/authz/policies/
├── common/   #  Helper methods used by the policy
├── authz/    # Application route Authorization Policies  
```


### 1️⃣ Local Policy Mount (authz-v1)

In this mode, the OPA container is started with policies mounted directly from the local filesystem.

**Docker Compose Service:**

```yaml
authz-service-v1:
  profiles: ["authz-v1"]
  image: openpolicyagent/opa:latest
  command: ["run", "--server", "--addr", "0.0.0.0:8181", "/policies"]
  volumes:
    - $PWD/deployment/authz/policies:/policies
```

**Start Command:**

```bash
make AUTHZ_PROFILE=authz-v1 authz_start
```

OPA will **immediately load and serve policies** found under `deployment/authz/policies`.

### 2️⃣ Remote Bundle Server (authz-v2)

In this mode, OPA loads its policies from a **remote bundle server** via a config file.

**Docker Compose Services:**

* `bundle-server`: Serves policy bundles from `deployment/authz/dist`
* `authz-service-v2`: Fetches and loads policies via `authz_config.yaml`

**OPA Config File:** `deployment/authz/config/authz_config.yaml`

```yaml
services:
  - name: bundle-server
    url: http://bundle-server:8888
bundles:
  authz:
    service: bundle-server
    resource: /bundle.tar.gz
    polling:
      min_delay_seconds: 300
      max_delay_seconds: 600
```


```bash
❯ AUTHZ_PROFILE=authz-v2 make start
docker compose --profile authz-v2 up -d
[+] Running 2/0
 ✔ Container bundle-server     Running                                                                                                                                                                                                          0.0s
 ✔ Container authz-service-v2  Running                                                                                                                                                                                                          0.0s
[+] Running 1/0
 ✔ Container simple-opa-integration  Running                                                                                                                                                                                                    0.0s
❯ make test.rego
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.

[notice] A new release of pip is available: 25.0.1 -> 25.1.1
[notice] To update, run: pip install --upgrade pip
🔐 Generated JWT:
 eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkphbmUgRG9lIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzUwODc3NDk4fQ.2thGSPs6t3AMZGAvW-XiXDHvDbyF-Sce4HaKK2b-WD8

📡 Sending request to OPA...

📥 OPA Response:
{"decision_id":"61ee564a-d5a3-4e79-9e08-5d06089208af","result":{"allow":false}}
```

**Start Command:**

```bash
make AUTHZ_PROFILE=authz-v2 authz_start
```

OPA will **fetch `bundle.tar.gz`** from the bundle server and load policies dynamically.

### 🪣 3️⃣ AWS S3 Bucket – Policy Bundle Deployment (authz-v3)
In this mode, OPA dynamically fetches policies from an S3 bucket, simulating a cloud-native deployment where policy bundles are managed in object storage. This reflects how production-grade services often fetch policy bundles from secured S3 buckets, governed by IAM roles for authorization.

In the POC setup, LocalStack is used to mock AWS services like S3 for local testing.

🚀 Start Command
To build policies, deploy to S3, and start the services:

```bash

❯ AUTHZ_PROFILE=authz-v3 make stop build.rego start deploy.rego test.rego.integration
[+] Running 2/2
 ✔ Container authz-service-s3  Removed                                                                                                                                                                                                          0.1s
 ✔ Container aws-mock-service  Removed                                                                                                                                                                                                          3.8s
[+] Running 1/1
 ✔ Container simple-opa-integration  Removed                                                                                                                                                                                                    0.6s
WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested
docker compose --profile authz-v3 up -d
[+] Running 3/3
 ✔ Container aws-mock-service                                                                                                                                      Started                                                                      0.1s
 ✔ Container authz-service-s3                                                                                                                                      Started                                                                      0.2s
 ! authz-service-s3 The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested                                                                              0.0s
[+] Running 1/1
 ✔ Container simple-opa-integration  Started                                                                                                                                                                                                    0.1s

[INFO] Deploying bundle.tar.gz to S3 Bucket

🪣 Creating bucket ...
make_bucket: simple-app
📦 Uploading bundle.tar.gz to s3://simple-app...
upload: ../authz/bundle.tar.gz to s3://simple-app/authz/bundle.tar.gz
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.

[notice] A new release of pip is available: 25.0.1 -> 25.1.1
[notice] To update, run: pip install --upgrade pip
🔐 Generated JWT:
 eyJhbGciOiJIUzI1NiIsImtpZCI6InNhbXBsZS1hcHAiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkphbmUgRG9lIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzUwOTE5NjQ4fQ.qvCvtfE77iRnH8SfpVpkGJkbQPV6ftPM4UfN8fWYvxE

📡 Sending request to OPA...

📥 OPA Response:
{"decision_id":"46275026-1757-4adc-8338-312108cf1239","result":{"allow":true}}
```

### 🔁 Switching Between Modes

Use the `AUTHZ_PROFILE` Makefile variable to switch between the two modes:

```bash
# Local policy mount
make AUTHZ_PROFILE=authz-v1 start

# Remote bundle via server
make AUTHZ_PROFILE=authz-v2 start

# AWS S3 bucket simulation via LocalStack
make AUTHZ_PROFILE=authz-v3 start
```


![OPA](docs/opa_deployment.png)

Rego policy for `GET` endpoint:

```rego
package simple.authz
import data.common.utils.is_valid_uuid
import data.common.utils.jwt.decode_token

default allow = false

allow if {
    claims := decode_token(input.token)
    claims.role in {"admin", "viewer"}
    input.method == "GET"
    input.path = ["api", "v1", "users", user_id]
    is_valid_uuid(user_id)
}

```

Figure 2 illustrates a API call to OPA using Postman

![Execution](docs/postman.png)

---

### 📚 References

* **[Open Policy Agent (OPA)](https://www.openpolicyagent.org/):** General-purpose policy engine used for authorization.
* **[Rego JWT Build in Function](https://docs.styra.com/opa/rego-by-example/builtins/io_jwt):** Rego's JWT Built-in Functions
* **[Rego](https://www.openpolicyagent.org/docs/latest/policy-language/):** Declarative language for defining policies in OPA.
* **[Sanic](https://sanic.dev/):** Python web framework used to build async APIs.
* **[Docker](https://www.docker.com/):** Used for containerizing and running the OPA server and services.


**Disclaimer**
This project is developed purely as a Proof of Concept (POC) for learning and demonstration purposes.

All references, documentation, and external materials used during development are listed in the References section. If any source has been unintentionally omitted, it is purely accidental.

This project is not intended for production use. 