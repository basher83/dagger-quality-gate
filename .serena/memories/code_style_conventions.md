# Code Style and Conventions

## Python Code Style
- **Line Length**: 100 characters (configured in ruff)
- **Target Python Version**: Python 3.10+
- **Linter**: Ruff (modern Python linter and formatter)
- **Type Checker**: MyPy with Python 3.10 target

## Ruff Configuration
```toml
[tool.ruff]
line-length = 100
target-version = "py310"
```

## MyPy Configuration
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
```

## Code Conventions
1. **Type Hints**: Use type hints for all function parameters and return values
2. **Docstrings**: Triple-quoted docstrings for classes and public methods
3. **Imports**: Standard library first, then third-party, then local imports
4. **Async/Await**: Use async/await for concurrent operations (via anyio)
5. **Data Classes**: Use Pydantic BaseModel for configuration and data validation
6. **Error Handling**: Provide clear error messages and preserve tool output

## Example Code Patterns
```python
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class CheckConfig(BaseModel):
    """Configuration for an individual check."""
    
    enabled: bool = True
    container_image: Optional[str] = None
    additional_args: List[str] = Field(default_factory=list)

async def run_check(client: Client, source: Directory, check_name: str) -> CheckResult:
    """Run a single quality check."""
    # Implementation here
```

## File Organization
- Main pipeline logic in `main.py`
- Configuration management in `config.py`
- Individual check implementations in `checks/` directory
- Each check type in its own module (e.g., `checks/python.py`, `checks/security.py`)
- Documentation in `docs/` directory
- Examples in `examples/` directory

## Naming Conventions
- Classes: PascalCase (e.g., `QualityGatePipeline`, `CheckResult`)
- Functions: snake_case (e.g., `run_check`, `load_config`)
- Constants: UPPER_SNAKE_CASE (e.g., `ENABLE_RUFF`)
- Private methods: prefix with underscore (e.g., `_run_parallel`)

## Important Notes
- DO NOT add comments unless specifically requested
- Follow existing patterns in the codebase
- Use Dagger Python SDK patterns and best practices
- Leverage asyncio for concurrent check execution