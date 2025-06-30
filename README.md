# dagger-quality-gate

A universal, reusable Dagger pipeline for running quality checks across any repository. Run the same checks locally and in CI with zero configuration changes.

## 🚀 Quick Start

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/basher83/dagger-quality-gate.git
cd dagger-quality-gate
uv sync

# Run quality checks
uv run python main.py /path/to/your/project
```

## 📋 Features

- **🔍 Multi-language support** - Python, Markdown, Terraform, and more
- **🛡️ Security scanning** - Detect vulnerabilities and exposed secrets
- **⚡ Fast execution** - Parallel checks with container isolation
- **🔧 Highly configurable** - Enable/disable checks via environment variables
- **🐳 Powered by Dagger** - Consistent execution locally and in CI
- **📦 Modern tooling** - Uses `uv` for fast Python package management

## 🧪 Supported Checks

| Category | Tools | Purpose |
|----------|-------|---------|
| **Python** | ruff, black, mypy, Ty | Linting, formatting, type checking |
| **Security** | Bandit, Semgrep, Safety | Vulnerability and dependency scanning |
| **Infrastructure** | Terraform fmt, TFLint | Infrastructure code quality |
| **Documentation** | markdownlint | Markdown formatting and style |
| **Secrets** | Gitleaks | Detect exposed credentials |

See [Available Checks](docs/checks.md) for detailed information.

## 📖 Documentation

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[Configuration Guide](docs/configuration.md)** - Environment variables and settings
- **[CI/CD Integration](docs/ci-integration.md)** - GitHub Actions, GitLab, Jenkins, and more
- **[Development Guide](docs/development.md)** - Adding new checks and contributing
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🎯 Basic Usage

```bash
# Run all checks (default)
uv run python main.py

# Run specific checks only
ENABLE_RUFF=true ENABLE_BLACK=true ENABLE_MYPY=true ENABLE_TY=true uv run python main.py

# Run with Task (if installed)
task test              # Test on example repo
task run              # Run on current directory
task test:python      # Test only Python checks
```

## ⚙️ Configuration Examples

```bash
# Disable specific checks
ENABLE_SAFETY=false uv run python main.py

# Run sequentially instead of parallel
PARALLEL=false uv run python main.py

# Get detailed output
VERBOSE=true uv run python main.py
```

See [Configuration Guide](docs/configuration.md) for all options.

## 🐳 CI/CD Integration

```yaml
# GitHub Actions
- name: Run Quality Gate
  uses: astral-sh/setup-uv@v3
- run: |
    uv sync
    uv run python main.py
```

See [CI/CD Integration Guide](docs/ci-integration.md) for more platforms.

## 🏗️ Project Structure

```
dagger-quality-gate/
├── main.py              # Pipeline orchestrator
├── config.py            # Configuration management
├── checks/              # Quality check implementations
├── docs/                # Documentation
├── examples/            # Test files with intentional issues
└── pyproject.toml       # Project configuration
```

## 🤝 Contributing

Contributions are welcome! See the [Development Guide](docs/development.md) for:
- Adding new quality checks
- Project architecture
- Testing guidelines
- Code style requirements

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Links

- [Dagger Documentation](https://docs.dagger.io/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Issue Tracker](https://github.com/basher83/dagger-quality-gate/issues)