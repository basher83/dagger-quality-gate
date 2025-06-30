# Task Completion Checklist

When completing any coding task in this project, always run the following commands:

## 1. Code Quality Checks

### Linting
```bash
# Check for linting issues
uv run python -m ruff check .

# Auto-fix linting issues if any
uv run python -m ruff check . --fix
```

### Code Formatting
```bash
# Format all Python code
uv run python -m ruff format .
```

### Type Checking
```bash
# Run MyPy type checker
uv run python -m mypy . --ignore-missing-imports
```

## 2. Test the Implementation
```bash
# Test on the example repository (should show intentional failures)
uv run python main.py examples/sample-repo

# Run on current directory to ensure no regressions
uv run python main.py .
```

## 3. Verify All Checks Pass
```bash
# Run the full CI simulation
task ci

# Or manually:
task install
task lint
task test
```

## 4. Check Git Status
```bash
# Review all changes
git status
git diff

# Stage changes if everything looks good
git add .
```

## Important Reminders
- NEVER commit unless explicitly asked by the user
- Always run lint and typecheck before considering task complete
- If unable to find the correct command, ask the user and suggest writing it to CLAUDE.md
- Ensure all checks pass before marking task as complete
- Test both positive cases (should pass) and negative cases (example repo should fail)