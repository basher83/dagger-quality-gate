# Suggested Commands for Dagger Quality Gate

## Installation and Setup
```bash
# Install uv package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

## Running the Pipeline
```bash
# Run all checks on current directory
uv run python main.py

# Run on specific directory
uv run python main.py /path/to/project

# Run specific checks only
ENABLE_RUFF=true ENABLE_BLACK=true ENABLE_MYPY=true ENABLE_TY=true uv run python main.py

# Run with verbose output
VERBOSE=true uv run python main.py

# Run sequentially instead of parallel
PARALLEL=false uv run python main.py
```

## Task Commands (if Task is installed)
```bash
# List available tasks
task

# Install dependencies
task install

# Run pipeline on current directory
task run

# Test on example repository (should show failures)
task test

# Test with verbose output
task test:verbose

# Test only Python checks
task test:python

# Test only security checks
task test:security

# Watch for changes and run pipeline
task dev:watch

# Simulate CI run
task ci
```

## Development Commands
```bash
# Run linters on this project
uv run python -m ruff check .
uv run python -m mypy . --ignore-missing-imports

# Auto-fix linting issues
uv run python -m ruff check . --fix

# Format code with ruff
uv run python -m ruff format .

# Or format with black (checks formatting in CI)
uv run python -m black .

# Clean up generated files
task clean
```

## Git Commands (Darwin/macOS)
```bash
# Standard git commands work normally on macOS
git status
git add .
git commit -m "message"
git push

# Check for changes
git diff
git log --oneline -10
```

## File Operations (Darwin/macOS)
```bash
# List files (macOS uses BSD ls)
ls -la

# Find files
find . -name "*.py"

# Search in files (prefer ripgrep if available)
rg "pattern" .
# or use grep
grep -r "pattern" .

# Create directories
mkdir -p path/to/directory

# Remove files/directories (be careful!)
rm -rf directory_name
```

## Environment Variables for Configuration
```bash
# Enable/disable specific checks
export ENABLE_RUFF=true
export ENABLE_BLACK=true
export ENABLE_MYPY=true
export ENABLE_TY=true
export ENABLE_BANDIT=true
export ENABLE_SAFETY=true
export ENABLE_SEMGREP=true
export ENABLE_GITLEAKS=true
export ENABLE_MARKDOWN=true
export ENABLE_TERRAFORM=true
export ENABLE_TFLINT=true

# Other configuration
export VERBOSE=true
export PARALLEL=false
export FAIL_FAST=true
```