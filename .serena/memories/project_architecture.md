# Project Architecture

## Directory Structure
```
dagger-quality-gate/
├── main.py              # Main pipeline orchestrator (entry point)
├── config.py            # Configuration management (env vars, defaults)
├── checks/              # Quality check implementations
│   ├── __init__.py
│   ├── base.py          # Base check interface
│   ├── markdown.py      # Markdown lint check
│   ├── python.py        # Python checks (ruff, mypy, Ty)
│   ├── security.py      # Security checks (Bandit, Semgrep, Safety)
│   ├── terraform.py     # Terraform checks (fmt, tflint)
│   └── secrets.py       # Secret scanning (Gitleaks)
├── docs/                # Documentation
│   ├── PRD.md           # Product Requirements Document
│   ├── checks.md        # Available checks documentation
│   ├── configuration.md # Configuration guide
│   ├── ci-integration.md # CI/CD integration guide
│   ├── development.md   # Development guide
│   ├── installation.md  # Installation instructions
│   └── troubleshooting.md # Common issues and solutions
├── examples/            # Test repositories
│   └── sample-repo/     # Example repo with intentional issues
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions workflow
├── pyproject.toml       # Project configuration and dependencies
├── Taskfile.yml         # Task automation
├── CLAUDE.md            # Claude AI assistant instructions
└── README.md            # Project documentation
```

## Core Components

### 1. Main Pipeline (`main.py`)
- `QualityGatePipeline` class: Main orchestrator
- Handles parallel/sequential execution
- Manages Dagger client connection
- Displays results in rich terminal UI

### 2. Configuration (`config.py`)
- `CheckConfig`: Individual check configuration
- `PipelineConfig`: Overall pipeline settings
- Environment variable parsing
- Default values and toggles

### 3. Check Modules (`checks/`)
Each check module implements:
- Async function to run the check
- Container setup with appropriate image
- Result parsing and error handling
- Returns `CheckResult` object

### 4. Execution Flow
1. Load configuration from environment variables
2. Initialize Dagger client connection
3. Mount source directory as Dagger Directory
4. Determine enabled checks
5. Execute checks (parallel or sequential)
6. Collect and display results
7. Return appropriate exit code

## Key Design Principles
1. **Container Isolation**: Each tool runs in its own container
2. **Modular Checks**: Easy to add/remove/modify checks
3. **Environment Configuration**: All settings via env vars
4. **Fail-fast Option**: Stop on first failure if configured
5. **Rich Output**: Clear, colorful terminal output with tables

## Supported Checks (MVP)
- **Python**: ruff, mypy, Ty
- **Security**: Bandit, Semgrep, Safety
- **Infrastructure**: Terraform fmt, TFLint
- **Documentation**: markdownlint
- **Secrets**: Gitleaks

## Future Extensibility
- Add new checks by creating modules in `checks/`
- Support for SARIF/JSON output formats
- Parametric configuration via TOML file
- Integration with more CI/CD platforms