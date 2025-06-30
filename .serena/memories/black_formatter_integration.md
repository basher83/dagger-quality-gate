# Black Formatter Integration

## Overview

Black formatter was added to the Python pipeline alongside existing tools (Ruff, Mypy, Ty, Bandit, Semgrep, Safety).

## Implementation Details

### Installation Method

- **Tool**: Black
- **Method**: `uv pip install --system black`
- **Important**: Do NOT use `uv tool install` for Black

### Configuration

Added to `config.py`:

```python
black: CheckConfig = Field(
    default_factory=lambda: CheckConfig(container_image="python:3.11-slim")
)
```

### Check Implementation

Located in `checks/python.py`:

- Runs in check mode: `black --check --diff .`
- Returns failure if formatting issues found
- Shows diff of what would be changed

### Environment Variable

- **Default**: Black is enabled by default
- `ENABLE_BLACK=false` to disable the check
- `ENABLE_BLACK=true` to explicitly enable (though it's already enabled by default)

## Usage Examples

```bash
# Run only Black check (all others explicitly disabled)
ENABLE_BLACK=true ENABLE_RUFF=false ENABLE_MYPY=false ENABLE_TY=false ENABLE_BANDIT=false ENABLE_SEMGREP=false ENABLE_SAFETY=false ENABLE_TERRAFORM=false ENABLE_TFLINT=false ENABLE_GITLEAKS=false ENABLE_MARKDOWN=false uv run python main.py

# Disable Black while running other Python checks
ENABLE_BLACK=false uv run python main.py

# Run all Python checks (all enabled by default, but can be explicit)
ENABLE_RUFF=true ENABLE_BLACK=true ENABLE_MYPY=true ENABLE_TY=true uv run python main.py

# Format code locally (not part of pipeline)
uv run python -m black .
```

## Integration Points

- Added to PipelineConfig in `config.py`
- Added to check lists in `load_config()` and `get_enabled_checks()`
- Added to Python checks in `main.py` `_run_check()` method
- Documented in all relevant documentation files
