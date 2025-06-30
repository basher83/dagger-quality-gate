# Available Quality Checks

This document provides detailed information about each quality check available in the pipeline.

## Markdown Checks

### markdownlint

**Tool**: [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)  
**Container**: `davidanson/markdownlint-cli2:latest`  
**Purpose**: Ensures consistent markdown formatting and style

Checks for:
- Line length limits
- Proper heading structure
- List formatting
- Trailing spaces
- File endings
- Link formatting

**Common Issues**:
```markdown
# Bad
## Heading without blank line above
- List without blank line above

# Good

## Heading with proper spacing

- List with proper spacing
```

## Python Checks

### ruff

**Tool**: [Ruff](https://github.com/astral-sh/ruff)  
**Installation**: `uv tool install ruff`  
**Purpose**: Fast Python linter that replaces flake8, isort, and more

Checks for:
- Unused imports and variables
- Code style (PEP 8)
- Import sorting
- Common bugs and anti-patterns
- Security issues

**Configuration**: Create `.ruff.toml` or `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py310"
```

### mypy

**Tool**: [mypy](https://github.com/python/mypy)  
**Installation**: `uv pip install --system mypy`  
**Purpose**: Static type checker for Python

Checks for:
- Type annotation correctness
- Missing type hints
- Type compatibility
- Return type consistency

**Configuration**: Create `mypy.ini` or use `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
```

### Ty

**Tool**: [Ty](https://github.com/astral-sh/ty)  
**Installation**: `uv tool install ty`  
**Purpose**: Modern Python type checker (alternative to mypy)

Checks for:
- Type safety
- Type inference
- Compatibility with Python typing features

## Security Checks

### Bandit

**Tool**: [Bandit](https://github.com/PyCQA/bandit)  
**Installation**: `uv pip install --system bandit[toml]`  
**Purpose**: Security linter for Python

Checks for:
- Hardcoded passwords
- SQL injection vulnerabilities
- Use of insecure functions
- Shell injection risks
- Weak cryptography

**Suppressing False Positives**:
```python
# nosec - Comment to suppress specific line
subprocess.call(user_input, shell=True)  # nosec B602
```

### Semgrep

**Tool**: [Semgrep](https://semgrep.dev/)  
**Container**: `returntocorp/semgrep:latest`  
**Purpose**: Static analysis for security and bug finding

Checks for:
- OWASP Top 10 vulnerabilities
- Language-specific security issues
- Custom security rules
- Code quality issues

**Configuration**: Uses `--config=auto` by default

### Safety

**Tool**: [Safety](https://github.com/pyupio/safety)  
**Installation**: `uv pip install --system safety`  
**Purpose**: Checks Python dependencies for known vulnerabilities

Checks for:
- Outdated packages with CVEs
- Insecure dependency versions
- License compliance (with paid version)

**Note**: Now uses `safety scan` command (not the deprecated `check`)

## Infrastructure Checks

### Terraform Format

**Tool**: terraform fmt  
**Container**: `hashicorp/terraform:latest`  
**Purpose**: Ensures consistent Terraform formatting

Checks for:
- Proper indentation
- Consistent spacing
- Canonical format

**Auto-fix**: Run without `-check` flag:
```bash
terraform fmt -recursive
```

### TFLint

**Tool**: [TFLint](https://github.com/terraform-linters/tflint)  
**Container**: `ghcr.io/terraform-linters/tflint:latest`  
**Purpose**: Terraform linter for best practices

Checks for:
- Deprecated syntax
- Unused declarations
- Missing required attributes
- Provider-specific issues

**Configuration**: Create `.tflint.hcl`:
```hcl
rule "terraform_required_providers" {
  enabled = true
}
```

## Secrets Scanning

### Gitleaks

**Tool**: [Gitleaks](https://github.com/gitleaks/gitleaks)  
**Container**: `zricethezav/gitleaks:latest`  
**Purpose**: Detects secrets in code

Checks for:
- API keys
- AWS credentials
- Private keys
- Passwords
- Tokens

**Configuration**: Create `.gitleaks.toml`:
```toml
[allowlist]
paths = [
  "test/fixtures"
]
```

**Ignoring False Positives**: Create `.gitleaksignore`:
```
# Format: <secret-hash>:<file>:<line>
abc123def456:config.py:42
```

## Adding Custom Checks

To add support for additional tools:

1. Create a new module in `checks/`
2. Implement the check function
3. Add configuration in `config.py`
4. Update `main.py` to call the check

See the [Development Guide](development.md) for detailed instructions.