# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Dagger-based quality gate pipeline** written in Python. It provides a universal, reusable pipeline for running standard quality checks (linting, security scanning, type checking) across any repository. The pipeline is designed to run identically in local development and CI environments.

## Project Status

✅ **Fully implemented** - The project is complete with all core functionality including:
- Main pipeline orchestrator (`main.py`)
- All quality check implementations in `checks/` directory
- Configuration management via environment variables
- Example repository with intentional issues for testing
- GitHub Actions CI integration
- Comprehensive documentation

## Architecture

### Current Structure

```
dagger-quality-gate/
├── main.py                # Main Dagger pipeline script
├── checks/
│   ├── markdown.py        # Markdown lint step
│   ├── python.py          # Ruff, mypy, Ty steps
│   ├── terraform.py       # Terraform fmt/tflint steps
│   ├── secrets.py         # Gitleaks step
│   ├── security.py        # Bandit, semgrep, safety
├── config.py              # Env var toggles & defaults
├── pipeline.toml          # (Stretch goal) Parametric config
└── examples/
    └── sample-repo/       # Demo repo for testing
```

### Key Design Principles

1. **Python SDK Only**: Use Dagger's Python SDK with asyncio
2. **Modular Checks**: Each check type in separate module for maintainability
3. **Environment Variables**: Configure checks via env vars (e.g., `ENABLE_RUFF=true`)
4. **Container-based**: Each tool runs in its own container
5. **Fail-fast**: Pipeline fails if any check fails

## Supported Checks

### MVP Checks
- **Markdown**: markdownlint (Node-based)
- **Python**: 
  - Linting: ruff
  - Formatting: black
  - Type checking: mypy + Ty (https://github.com/astral-sh/ty)
  - Security: Bandit, semgrep, safety
- **Terraform**: terraform fmt -check, tflint
- **Secrets**: gitleaks

### Future Checks
- YAML: yamllint
- Dockerfile: hadolint
- Shell: shellcheck

## Development Commands

```bash
# Install dependencies with uv
uv sync

# Run the pipeline locally
uv run python main.py

# Run with specific checks enabled
ENABLE_RUFF=true ENABLE_BLACK=true ENABLE_MYPY=true ENABLE_TY=true uv run python main.py

# Run on a specific directory
uv run python main.py /path/to/project

# Run with verbose output
VERBOSE=true uv run python main.py
```

## Implementation Guidelines

When working with this project:

1. **Use Dagger Python SDK**: Follow Dagger's Python SDK patterns and best practices
2. **Async/Await**: Leverage asyncio for concurrent check execution
3. **Container Management**: Each tool should run in appropriate container (e.g., Python tools in Python container)
4. **Error Handling**: Provide clear error messages and preserve tool output
5. **Configuration**: Use environment variables for toggles, with sensible defaults in config.py

## Testing Approach

- Create example repositories in `examples/` with intentional issues
- Ensure pipeline correctly identifies problems in test repos
- Test both local and CI execution paths

## CI Integration

The pipeline should work seamlessly with GitHub Actions (and other CI systems):
- Provide example `.github/workflows/ci.yml`
- Ensure proper exit codes for CI integration
- Support both push and pull request triggers

## Python Tools Installation

**IMPORTANT**: Different Python tools require different installation methods with `uv`:

| Tool | Installation Method | Command |
|------|-------------------|---------|
| **Black** | uv pip install | `uv pip install --system black` |
| **Ruff** | uv tool install (preferred) or pip | `uv tool install ruff` |
| **Ty** | uv tool install | `uv tool install ty` |
| **Mypy** | uv pip install | `uv pip install --system mypy` |
| **Bandit** | uv pip install | `uv pip install --system bandit` |
| **Semgrep** | uv pip install | `uv pip install --system semgrep` |
| **Safety** | uv pip install | `uv pip install --system safety` |

**Key Implementation Notes**:
- Tools installed with `uv tool install` are located at: `/root/.local/share/uv/tools/{tool_name}/bin/{tool_name}`
- Tools installed with `uv pip install --system` are available directly in PATH
- Always use the correct installation method to avoid runtime errors