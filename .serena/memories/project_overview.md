# Dagger Quality Gate - Project Overview

## Purpose
Universal, reusable Dagger pipeline for running quality checks across any repository. It provides a consistent way to run linting, security scanning, type checking, and other quality checks both locally and in CI environments.

## Key Features
- Multi-language support (Python, Markdown, Terraform, etc.)
- Security scanning for vulnerabilities and exposed secrets
- Parallel execution with container isolation
- Highly configurable via environment variables
- Powered by Dagger for consistent execution
- Modern Python tooling with `uv` package manager

## Tech Stack
- **Language**: Python 3.10+
- **Container Platform**: Dagger (Python SDK)
- **Package Manager**: uv (Astral's fast Python package manager)
- **Dependencies**:
  - dagger-io>=0.9.0 (Container orchestration)
  - anyio>=4.0.0 (Async support)
  - rich>=13.0.0 (Terminal UI)
  - pydantic>=2.0.0 (Data validation)
  - typing-extensions>=4.0.0
  - opentelemetry-exporter-otlp-proto-grpc>=1.34.0 (Observability)

## Development Dependencies
- ruff>=0.1.0 (Linting and formatting)
- mypy>=1.0.0 (Type checking)
- pytest>=7.0.0 (Testing)

## Current Status
✅ **Fully implemented** - The project has complete implementation code including:
- Main pipeline orchestrator (`main.py`)
- All check implementations in `checks/` directory
- Configuration management (`config.py`)
- Full documentation and examples
- CI/CD integration with GitHub Actions