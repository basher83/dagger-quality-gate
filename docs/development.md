# Development Guide

This guide explains how to extend the Dagger Quality Gate pipeline with new checks and contribute to the project.

## Project Structure

```
dagger-quality-gate/
├── main.py                # Main pipeline orchestrator
├── config.py              # Configuration management
├── checks/               # Check implementations
│   ├── __init__.py
│   ├── base.py          # Base utilities for checks
│   ├── markdown.py       # Markdown linting
│   ├── python.py         # Python checks (ruff, mypy, Ty)
│   ├── security.py       # Security scans (Bandit, Semgrep, Safety)
│   ├── terraform.py      # Terraform checks
│   └── secrets.py        # Secrets scanning
├── pyproject.toml       # Project configuration and dependencies
├── Taskfile.yml         # Task runner configuration
└── examples/            # Example test repository
```

## Adding a New Check

### Step 1: Create the Check Module

Create a new file in `checks/` directory:

```python
# checks/eslint.py
"""JavaScript/TypeScript linting using ESLint."""

from dagger import Client, Directory
from config import CheckConfig
from main import CheckResult


async def run_eslint_check(
    client: Client,
    source: Directory,
    config: CheckConfig
) -> CheckResult:
    """Run ESLint on JavaScript/TypeScript files."""
    try:
        # Create container with Node.js
        container = (
            client.container()
            .from_(config.container_image or "node:18-alpine")
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
        )
        
        # Install ESLint
        container = container.with_exec(["npm", "install", "-g", "eslint"])
        
        # Build command
        cmd = ["eslint", ".", "--ext", ".js,.jsx,.ts,.tsx"]
        cmd.extend(config.additional_args)
        
        # Run ESLint
        result = await container.with_exec(cmd).sync()
        
        try:
            output = await result.stdout()
            await result.exit_code()  # Will raise if non-zero
            return CheckResult("eslint", True, output=output)
        except Exception:
            # Get output for error details
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()
            return CheckResult(
                "eslint",
                False,
                output=stdout,
                error=stderr or stdout or "ESLint found issues"
            )
    
    except Exception as e:
        return CheckResult(
            "eslint",
            False,
            error=f"Failed to run ESLint: {str(e)}"
        )
```

### Step 2: Add Configuration

Update `config.py` to include the new check:

```python
# In PipelineConfig class
eslint: CheckConfig = Field(
    default_factory=lambda: CheckConfig(
        container_image="node:18-alpine"
    )
)

# In get_enabled_checks function
for check_name in [
    "markdown", "ruff", "mypy", "ty", "bandit",
    "semgrep", "safety", "terraform", "tflint", "gitleaks",
    "eslint"  # Add new check here
]:
```

### Step 3: Update Main Pipeline

Update `main.py` to call the new check:

```python
# In _run_check method
elif check_name == "eslint":
    from checks.eslint import run_eslint_check
    return await run_eslint_check(client, source, check_config)
```

### Step 4: Test the New Check

Create test files and run:

```bash
# Test only the new check
ENABLE_ESLINT=true ENABLE_MARKDOWN=false ENABLE_RUFF=false ... uv run python main.py
```

## Using uv in Containers

The project uses `uv` for Python package management. Here's how to use it in check containers:

### For Python Tools

```python
from .base import prepare_python_container_with_uv

# Prepare container with uv installed
container = prepare_python_container_with_uv(container)

# Install tools
# Option 1: uv tool install (for standalone tools)
container = container.with_exec(["uv", "tool", "install", "ruff"])
# Tool will be at: /root/.local/share/uv/tools/ruff/bin/ruff

# Option 2: uv pip install --system (for libraries)
container = container.with_exec(["uv", "pip", "install", "--system", "mypy"])
# Tool will be in system PATH
```

## Development Workflow

### Local Development

1. **Set up environment**:
   ```bash
   uv sync
   ```

2. **Run tests**:
   ```bash
   task test
   ```

3. **Lint your code**:
   ```bash
   task lint
   ```

4. **Format code**:
   ```bash
   task format
   ```

### Testing Changes

1. **Test on example repository**:
   ```bash
   task test
   ```

2. **Test on real project**:
   ```bash
   uv run python main.py /path/to/project
   ```

3. **Test specific checks**:
   ```bash
   ENABLE_MYCHECK=true ENABLE_OTHERS=false uv run python main.py
   ```

## Best Practices

### 1. Container Images

- Use official images when available
- Use Alpine variants for smaller size
- Pin versions for reproducibility

```python
config.container_image or "tool:1.2.3-alpine"
```

### 2. Error Handling

Always provide clear error messages:

```python
try:
    # Run check
except Exception as e:
    return CheckResult(
        check_name,
        False,
        error=f"Specific error description: {str(e)}"
    )
```

### 3. Output Handling

- Capture both stdout and stderr
- Truncate very long output
- Provide actionable error messages

### 4. Performance

- Use appropriate container sizes
- Cache dependencies when possible
- Consider parallel execution impact

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all checks pass
5. Update documentation
6. Submit PR with clear description

### Code Style

- Follow PEP 8 (enforced by ruff)
- Add type hints (checked by mypy)
- Write clear docstrings
- Keep functions focused and small

### Documentation

- Update relevant docs in `docs/`
- Add examples for new features
- Update README if needed
- Include configuration examples

## Advanced Topics

### Custom Base Images

Create optimized base images with tools pre-installed:

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv pip install --system ruff mypy
```

### Parallel Execution

Checks run in parallel by default. Consider:
- Resource usage
- Container startup time
- Network dependencies

### Caching Strategies

For faster execution:
- Cache tool installations
- Use Dagger's cache mounts
- Pre-build common base images

## Getting Help

- Check existing issues on GitHub
- Join the Dagger community
- Read Dagger documentation
- Ask questions in discussions