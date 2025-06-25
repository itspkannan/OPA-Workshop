# Simple OPA Integration Project

## 🔍 Project Overview

This Python project is a **proof of concept** demonstrating the integration of [Open Policy Agent (OPA)](https://www.openpolicyagent.org/) for **authorization of a REST API**. It showcases best practices in dependency management, linting, testing, and containerization using modern Python tooling.

---

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

---

## 🚀 Usage

```bash
❯ make help

Available commands:
  app_start       Start App
  app_stop        Stop App
  authz_start     Start Authorization Service(Open Policy Agent)
  authz_stop      Stop Authorization Service(Open Policy Agent)
  cleanup         Cleanup the developmenet environment temporary files
  docker_build    Build application docker image
  dockerfile_lint Run lint for dockerfile
  format          Format code using Ruff (Black-compatible)
  help            Help message
  infra_cleanup   Cleanup the infrastructure
  infra_init      Create the infrastructure
  init            Initialize the Poetry development environment
  lint            Run static analysis with Ruff and Mypy
  start           Start Authorization Services and Application
  stop            Start Authorization Services and Application
  test            Run tests with Pytest and show coverage
  validate_policy Validate Rego Policies
```
