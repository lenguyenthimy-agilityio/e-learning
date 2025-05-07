# Backend Improving — E-Learning API System

This project is designed to **enhance backend development skills** by building a production-grade API system for an e-learning platform. It emphasizes best practices in Django, DRF, testing, linting, and modern Python tooling.

---

## Prerequisites

Make sure you have the following tools installed:

-   [**uv**](https://docs.astral.sh/uv) – Fast Python package manager and environment manager
-   [**pre-commit**](https://pre-commit.com/) – Framework for managing Git hooks
-   [**ruff**](https://docs.astral.sh/ruff/) – Ultra-fast Python linter and formatter

---

## Stack & Versioning

### Core Versions

-   **Python**: 3.13
-   **Django**: 5.2
-   **Django REST Framework**: 3.16.0

### ⚙️ Technical Stack

-   [Django REST Framework](https://www.django-rest-framework.org/)
-   [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/) – OpenAPI 3 schema generation
-   [pytest](https://docs.pytest.org/en/stable/) – Testing framework
-   [pytest-django](https://pytest-django.readthedocs.io/en/latest/)
-   [factory-boy](https://factoryboy.readthedocs.io/en/stable/) – Test data factories

---

## Development Setup

### Using `uv`

1. **Install `uv`** (macOS/Linux):

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. Setup environments: create `.env` file follow `.env.example` file with your own settings

3. Create the env with uv

    ```bash
    uv venv .venv
    ```

4. Install dependencies

    ```bash
    uv sync
    ```

5. Activate the environment

    ```bash
    source .venv/bin/activate
    ```

6. Install git hooks

    ```bash
    pre-commit install
    ```

7. Start the server

    ```bash
    bin/dj-run.sh
    ```

### Run with Docker compose

1. Build docker images

    ```bash
    docker-compose build
    ```

2. Get Docker compose up

    ```bash
    docker-compose up
    ```

    Go to [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/) to view all APIs.

### API documentation

Go to [http://localhost:8000/api/v1/docs/swagger/](http://localhost:8000/api/v1/docs/swagger/) to view all document APIs.

## Commands:

### uv

-   Add package
    -   Add to project: `uv add <package-name>`
    -   Add to `dev` group: `uv add --dev <dev-package-name>`
-   Install packages:
    -   Install all packages: `uv sync`
    -   Install except dev packages: `uv sync --no-group dev`
-   Run command in virtual environment: `uv run <command>`
-   Ruff check: `ruff check`

### pre-commit

-   Install hook scripts: `pre-commit install`
-   Run pre-commit: `pre-commit run --all-files`
