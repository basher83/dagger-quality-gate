# Troubleshooting Guide

This guide helps resolve common issues when using the Dagger Quality Gate pipeline.

## Installation Issues

### uv: command not found

**Problem**: The `uv` command is not available after installation.

**Solution**:
```bash
# Reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add to your shell profile)
export PATH="$HOME/.cargo/bin:$PATH"

# Verify installation
uv --version
```

### Docker not running

**Problem**: Error message about Docker daemon not running.

**Solution**:
```bash
# Start Docker
# macOS: Open Docker Desktop
# Linux:
sudo systemctl start docker

# Verify Docker is running
docker ps
```

### OpenTelemetry errors

**Problem**: `RuntimeError: Requested component 'otlp_proto_grpc' not found`

**Solution**: Already fixed in the project. If you encounter this:
```bash
# Ensure dependencies are up to date
uv sync
```

## Check-Specific Issues

### Ruff: "process did not complete successfully: exit code: 1"

**Problem**: Ruff is finding linting issues (this is expected behavior).

**Solution**: 
- Review the errors in Dagger Cloud trace
- Fix the issues in your code
- Or disable specific rules in `.ruff.toml`

### Safety: "DEPRECATED: this command (`check`) has been DEPRECATED"

**Problem**: Using old safety command.

**Solution**: Already fixed - uses `safety scan` now. Update to latest version:
```bash
uv sync
```

### Terraform: "exit code: 3"

**Problem**: Terraform files are not properly formatted.

**Solution**:
```bash
# Auto-format your terraform files
terraform fmt -recursive
```

### MyPy: "No module named 'X'"

**Problem**: MyPy can't find imported modules.

**Solution**:
```bash
# Add to mypy configuration
[tool.mypy]
ignore_missing_imports = true

# Or install type stubs
uv pip install types-requests types-pyyaml
```

## Container Issues

### "exec: 'uv': executable file not found in $PATH"

**Problem**: uv is not available in the container.

**Solution**: This is already handled by the `prepare_python_container_with_uv` function. If you see this in custom checks, ensure you're using the base utility.

### Out of memory

**Problem**: Pipeline crashes or hangs during parallel execution.

**Solution**:
```bash
# Run checks sequentially
PARALLEL=false uv run python main.py

# Or increase Docker memory limit
```

### Slow container startup

**Problem**: Checks take a long time to start.

**Solution**:
- Use smaller base images (Alpine variants)
- Pre-pull common images
- Consider creating custom base images

## CI/CD Issues

### GitHub Actions: "uv: command not found"

**Problem**: uv not available in CI.

**Solution**: Use the official setup action:
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v3
```

### Permission denied in CI

**Problem**: Can't write to directories or install packages.

**Solution**:
```yaml
# Run as root in container
container:
  options: --user root
```

### Timeout in CI

**Problem**: Pipeline exceeds CI timeout limit.

**Solution**:
```yaml
# Increase timeout
timeout-minutes: 30

# Or run fewer checks
env:
  ENABLE_SAFETY: 'false'
  ENABLE_SEMGREP: 'false'
```

## Debug Techniques

### 1. View Dagger Cloud Traces

Access detailed execution logs:
1. Run the pipeline
2. Look for the trace URL in output
3. Visit https://dagger.cloud/... to see detailed logs

### 2. Enable Verbose Mode

```bash
VERBOSE=true uv run python main.py
```

### 3. Run Single Check

Isolate issues by running one check at a time:
```bash
# Only run ruff
ENABLE_RUFF=true ENABLE_MYPY=false ENABLE_SAFETY=false ... uv run python main.py
```

### 4. Check Container Logs

For custom debugging, modify the check to output more info:
```python
# Add debug output
debug_output = await container.with_exec(["ls", "-la"]).stdout()
print(f"Debug: {debug_output}")
```

### 5. Test in Container

Reproduce issues locally:
```bash
# Start a container with same image
docker run -it --rm -v $(pwd):/src -w /src python:3.11-slim bash

# Try commands manually
apt-get update && apt-get install -y curl
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="/root/.local/bin:$PATH"
uv --version
```

## Common Error Messages

### "Only one live display may be active at once"

**Problem**: Rich console conflict in parallel mode.

**Solution**: Already fixed. Update to latest version.

### "Distribution not found at: file:///src/astral-sh/ruff"

**Problem**: Wrong syntax for uv tool install.

**Solution**: Use correct package names:
```bash
# Correct
uv tool install ruff

# Wrong
uv tool install astral-sh/ruff
```

### "No virtual environment found"

**Problem**: uv pip needs a venv or --system flag.

**Solution**: Already fixed with `--system` flag.

## Performance Optimization

### Reduce Parallel Load

```bash
# Limit parallelism
PARALLEL=false uv run python main.py
```

### Skip Expensive Checks

```bash
# Skip slow checks during development
ENABLE_SEMGREP=false ENABLE_SAFETY=false uv run python main.py
```

### Use Task Commands

```bash
# Pre-configured for common scenarios
task test:python  # Only Python checks
task test:security  # Only security checks
```

## Getting Help

1. **Check Dagger Cloud traces** - Most detailed error information
2. **Read the error message carefully** - Often indicates the exact issue
3. **Search existing issues** - Someone may have encountered it before
4. **Ask in Dagger community** - For Dagger-specific issues
5. **Open an issue** - Include full error output and reproduction steps