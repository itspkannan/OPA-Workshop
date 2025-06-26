# Simple OPA Integration Project

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
  app_logs        View application logs
  app_start       Start App
  app_stop        Stop App
  authz_logs      View logs of Authorization Service (Open Policy Agent)
  authz_start     Start Authorization Service (Open Policy Agent)
  authz_stop      Stop Authorization Service (Open Policy Agent)
  cleanup         Cleanup the developmenet environment temporary files
  docker_build    Build application docker image
  docker_image_view View Application docker image view
  dockerfile_lint Run lint for dockerfile
  format          Format code using Ruff (Black-compatible)
  help            Help message
  infra_cleanup   Cleanup the infrastructure
  infra_init      Create the infrastructure
  init            Initialize the Poetry development environment
  lint            Run static analysis with Ruff and Mypy
  policy_build    Build policies into a gzipped file
  policy_check    Run OPA check on Policies
  policy_eval     Evaluate the Rego Policies
  policy_test     Test the policy against with a valid input
  runtime_view    view the active docker container
  start           Start Authorization Services and Application
  stop            Start Authorization Services and Application
  test            Run tests with Pytest and show coverage
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

**Start Command:**

```bash
make AUTHZ_PROFILE=authz-v2 authz_start
```

OPA will **fetch `bundle.tar.gz`** from the bundle server and load policies dynamically.

### 🔁 Switching Between Modes

Use the `AUTHZ_PROFILE` Makefile variable to switch between the two modes:

```bash
# Local policy mount
make AUTHZ_PROFILE=authz-v1 start

# Remote bundle via server
make AUTHZ_PROFILE=authz-v2 start
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

```bash
❯ AUTHZ_PROFILE=authz-v2 make start
docker compose --profile authz-v2 up -d
[+] Running 2/0
 ✔ Container bundle-server     Running                                                                                                                                                                                                          0.0s
 ✔ Container authz-service-v2  Running                                                                                                                                                                                                          0.0s
[+] Running 1/0
 ✔ Container simple-opa-integration  Running                                                                                                                                                                                                    0.0s
❯ make policy_test
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.

[notice] A new release of pip is available: 25.0.1 -> 25.1.1
[notice] To update, run: pip install --upgrade pip
🔐 Generated JWT:
 eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkphbmUgRG9lIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzUwODc3NDk4fQ.2thGSPs6t3AMZGAvW-XiXDHvDbyF-Sce4HaKK2b-WD8

📡 Sending request to OPA...

📥 OPA Response:
{"decision_id":"61ee564a-d5a3-4e79-9e08-5d06089208af","result":{"allow":false}}
```

---

### 📚 References

* **[Open Policy Agent (OPA)](https://www.openpolicyagent.org/):** General-purpose policy engine used for authorization.
* **[Rego](https://www.openpolicyagent.org/docs/latest/policy-language/):** Declarative language for defining policies in OPA.
* **[Sanic](https://sanic.dev/):** Python web framework used to build async APIs.
* **[Docker](https://www.docker.com/):** Used for containerizing and running the OPA server and services.


**Disclaimer**
This project is developed purely as a Proof of Concept (POC) for learning and demonstration purposes.

All references, documentation, and external materials used during development are listed in the References section. If any source has been unintentionally omitted, it is purely accidental.

This project is not intended for production use. 