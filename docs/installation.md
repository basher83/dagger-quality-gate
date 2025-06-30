# Installation Guide

This guide covers how to install and set up the Dagger Quality Gate pipeline.

## Prerequisites

Before installing, ensure you have the following:

- **Python 3.10+** - Required for running the pipeline
- **Docker** - Required for Dagger to run containers
- **uv** - Fast Python package manager ([installation instructions](https://github.com/astral-sh/uv#installation))
- **Dagger CLI** - Automatically installed by the Python SDK

### Installing uv

uv is a modern, fast Python package manager that replaces pip and other Python tools:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip (if you prefer)
pip install uv
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/basher83/dagger-quality-gate.git
cd dagger-quality-gate
```

### 2. Install Dependencies

Use uv to install all Python dependencies:

```bash
uv sync
```

This will:
- Create a virtual environment in `.venv/`
- Install all dependencies from `pyproject.toml`
- Generate a `uv.lock` file for reproducible builds

### 3. (Optional) Install Task Runner

For easier command execution, install Task:

```bash
# macOS
brew install go-task/tap/go-task

# Linux
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d

# Windows
scoop install task
```

## Verifying Installation

Run a test to ensure everything is installed correctly:

```bash
# Using Task
task test

# Or directly with uv
uv run python main.py examples/sample-repo/
```

You should see the pipeline run and report failures for the intentional issues in the example repository.

## Next Steps

- Read the [Configuration Guide](configuration.md) to learn about customizing checks
- See [CI Integration](ci-integration.md) for setting up in your CI/CD pipeline
- Check [Available Checks](checks.md) for detailed information about each quality check