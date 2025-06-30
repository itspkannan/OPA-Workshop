# Open Policy Agent Authorization Workshop

A hands-on workshop project to explore modern authorization using [Open Policy Agent (OPA)](https://www.openpolicyagent.org/) and Rego policies.

## Project 1: RestAPI Authorization using OPA

**Goal**: Use OPA to enforce basic access control based on HTTP method, path, and user role (via header).

The project demonstrates 3 deployment of rego policies where a JWT token is used as authenticated user with a valid token.

- Load the Rego Policies from local file system
- Build the policies into a deployable gzipped file and served to OPA via remote services.
- Build the policies into a deployable gzipped file and served to AWS S3 ( for pod using localstack S3).

All of above is deployed via docker compose as a mean of demonstration of integration of microservice and OPA

## Project 2: Integration of Oauth2 + OIDC provider to OPA for Rest API Authorization

**TODO**

**Goal**: Extend project 1 to demontrate a OPA + Oauth2/OIDC Provider integration

- Create Keycloak deployment
- Integrate the app to generate JWT token and authorize using OPA + Oauth2 provider.


## Project 3: RestAPI Authorization using OPA - Kubernetes Deployment

**Goal**: Extend project 1 to demontrate a OPA Sidecar deployment in Kubernetes using K3d.

- Create K3d cluster.
- Create helm deployment charts for the app.
- Deploy to AWS S3 policy bundle and integrate to OPA.


## Project 4: RestAPI Authorization using OPA  + Oauth2/OIDC provider - Kubernetes Deployment

**TODO**

**Goal**: Extend project 1 to demontrate a OPA Sidecar deployment in Kubernetes using K3d with Oauth2 provider integration.

- Combine the work done in Project 2 and Project 3


## Project 5: RestAPI Authorization using OPA  + Oauth2/OIDC provider - Kubernetes Deployment

**TODO**

**Goal**: Implement Project 4 using a Java Framework ( eg Spring).

