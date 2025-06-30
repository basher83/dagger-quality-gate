# Configuration Guide

The Dagger Quality Gate pipeline is highly configurable through environment variables. This guide covers all available configuration options.

## General Settings

These settings control the overall behavior of the pipeline:

| Variable | Default | Description |
|----------|---------|-------------|
| `FAIL_FAST` | `true` | Stop pipeline execution on first check failure |
| `PARALLEL` | `true` | Run checks in parallel for faster execution |
| `VERBOSE` | `false` | Enable verbose output with detailed check results |

### Examples

```bash
# Run checks sequentially
PARALLEL=false uv run python main.py

# Continue running all checks even if some fail
FAIL_FAST=false uv run python main.py

# Get detailed output
VERBOSE=true uv run python main.py
```

## Check-Specific Settings

### Enabling/Disabling Checks

All checks are **enabled by default**. To disable specific checks, set their environment variable to `false`:

| Check | Environment Variable |
|-------|---------------------|
| Markdown Linting | `ENABLE_MARKDOWN` |
| Python Linting (ruff) | `ENABLE_RUFF` |
| Python Type Checking (mypy) | `ENABLE_MYPY` |
| Python Type Checking (Ty) | `ENABLE_TY` |
| Security Scanning (Bandit) | `ENABLE_BANDIT` |
| Security Scanning (Semgrep) | `ENABLE_SEMGREP` |
| Dependency Scanning (Safety) | `ENABLE_SAFETY` |
| Terraform Formatting | `ENABLE_TERRAFORM` |
| Terraform Linting | `ENABLE_TFLINT` |
| Secrets Scanning | `ENABLE_GITLEAKS` |

### Examples

```bash
# Run only Python checks
ENABLE_MARKDOWN=false ENABLE_TERRAFORM=false ENABLE_TFLINT=false ENABLE_GITLEAKS=false uv run python main.py

# Disable type checking
ENABLE_MYPY=false ENABLE_TY=false uv run python main.py

# Run only security checks
ENABLE_MARKDOWN=false ENABLE_RUFF=false ENABLE_MYPY=false ENABLE_TY=false ENABLE_TERRAFORM=false ENABLE_TFLINT=false uv run python main.py
```

### Custom Container Images

You can override the default container image for any check:

```bash
# Use a specific Python version for ruff
RUFF_IMAGE=python:3.12-slim uv run python main.py

# Use a custom semgrep image
SEMGREP_IMAGE=returntocorp/semgrep:1.45.0 uv run python main.py
```

### Additional Arguments

Pass additional command-line arguments to any check:

```bash
# Add custom ruff configuration
RUFF_ARGS="--config=/path/to/ruff.toml" uv run python main.py

# Configure markdownlint to fix issues
MARKDOWN_ARGS="--fix" uv run python main.py

# Add custom semgrep rules
SEMGREP_ARGS="--config=p/security-audit --config=p/python" uv run python main.py
```

## Configuration in CI/CD

Environment variables work seamlessly in CI/CD environments:

### GitHub Actions

```yaml
- name: Run Quality Gate
  run: uv run python main.py
  env:
    ENABLE_MARKDOWN: 'true'
    ENABLE_RUFF: 'true'
    ENABLE_MYPY: 'true'
    VERBOSE: 'true'
    RUFF_ARGS: '--config=.ruff.toml'
```

### GitLab CI

```yaml
quality-gate:
  variables:
    ENABLE_SAFETY: 'false'
    PARALLEL: 'false'
  script:
    - uv run python main.py
```

## Configuration File (Future)

While not yet implemented, future versions will support a `pipeline.toml` configuration file for more complex setups:

```toml
[general]
fail_fast = true
parallel = true

[checks.ruff]
enabled = true
image = "python:3.11-slim"
args = ["--config", ".ruff.toml"]

[checks.mypy]
enabled = true
args = ["--strict"]
```

## Best Practices

1. **Start with defaults** - The default configuration runs all checks, which is usually what you want
2. **Disable incrementally** - Only disable checks that don't apply to your project
3. **Use Task commands** - The Taskfile provides pre-configured command combinations
4. **Document exceptions** - If you disable checks, document why in your project README
5. **Version control settings** - Consider creating a `.env` file for project-specific settings