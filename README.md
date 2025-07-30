# Open Policy Agent Authorization Workshop

A hands-on workshop project to explore modern authorization using [Open Policy Agent (OPA)](https://www.openpolicyagent.org/) and Rego policies.

---

## Project 1: ✅ RestAPI Authorization using OPA

**Goal**: Use OPA to enforce basic access control based on HTTP method, path, and user role (via header).

The project demonstrates 3 deployment modes of Rego policies where a JWT token is used as an authenticated user with a valid token.

- Load the Rego policies from local file system.
- Build the policies into a deployable gzipped bundle served to OPA via a remote service.
- Store and serve policies from AWS S3 (emulated using LocalStack).

All of the above is deployed via Docker Compose to demonstrate integration of microservices with OPA.

---

## Project 2: ✅ RestAPI Authorization using OPA – Kubernetes Deployment

**Goal**: Extend Project 1 to demonstrate OPA sidecar deployment in Kubernetes using K3d.

- Create a K3d cluster.
- Define Helm charts for the microservice + OPA sidecar.
- Deploy policy bundles via AWS S3 and integrate them with OPA.

---

## Project 3: 🔄 RestAPI Authorization using OPA + OAuth2/OIDC Provider – Kubernetes Deployment

**Goal**: Extend Project 2 by integrating OPA with an OAuth2/OIDC provider.

- Combine previous projects into a unified Python-based app using Sanic.
- Include JWT validation and claim-based policy enforcement.
- Test deployments via K3d and sidecar OPA.

---

## Project 4: ❌ RestAPI Authorization using OPA + OAuth2/OIDC Provider – Java Framework

**Goal**: Replicate Project 3 using a Java framework (e.g., Spring Boot or Quarkus).


---

### Legend:
* ✅ `Done`
* 🔄 `In Progress`
* ❌ `Not Started`
