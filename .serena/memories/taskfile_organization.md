# Taskfile Organization and Best Practices

## Overview

The Taskfile.yml provides a comprehensive set of commands for development and testing of the dagger-quality-gate project.

## Key Design Decisions

### 1. DRY Principle with Variables

Instead of YAML anchors (which Task doesn't support at root level), we use Task variables:

```yaml
vars:
  PYTHON: uv run python
  EXAMPLE_DIR: examples/sample-repo
  ALL_DISABLED: |
    ENABLE_BLACK=false \
    ENABLE_RUFF=false \
    ENABLE_MYPY=false \
    # ... all checks disabled
```

This allows individual tasks to be concise:
```yaml
test:black:
  desc: Test only Black formatter
  cmds:
    - '{{.ALL_DISABLED}} ENABLE_BLACK=true {{.PYTHON}} main.py {{.EXAMPLE_DIR}}'
```

### 2. Clear Namespace Separation

- `test:*` - Run checks on the example repository (with intentional issues)
- `check:*` - Run checks on the current project
- No duplicate functionality (removed redundant `dev` task)

### 3. Task Categories

#### Individual Check Tasks
- `test:black`, `test:ruff`, `test:mypy`, etc.
- Each enables only one specific check

#### Combination Tasks
- `test:python` - All Python checks (Black, Ruff, MyPy, Ty)
- `test:security` - All security checks (Bandit, Semgrep, Safety, Gitleaks)
- `test:terraform` - Infrastructure checks
- `test:fast` - Quick checks excluding slow security scanners

#### Project Check Tasks
- `check` - Run all checks on current project
- `check:python` - Python checks on current project
- `check:security` - Security checks on current project
- `check:fast` - Fast checks with PARALLEL=false for stability

## Usage Patterns

### Testing a New Check Implementation
```bash
# Test only the new check on example repo
task test:mycheck

# Test on current project
task check
```

### Development Workflow
```bash
# Quick feedback during development
task check:fast

# Full validation before commit
task check

# Watch mode for continuous feedback
task check:watch
```

### Debugging Pipeline Issues
```bash
# Test individual checks to isolate problems
task test:black
task test:ruff

# Run with verbose output
task test:verbose
```

## Maintenance Guidelines

1. **Adding New Checks**
   - Add to `ALL_DISABLED` variable
   - Create `test:newcheck` task
   - Update combination tasks if appropriate

2. **Modifying Defaults**
   - Update only the `ALL_DISABLED` variable
   - All tasks automatically inherit the change

3. **Performance Considerations**
   - `check:fast` disables PARALLEL for stability
   - Consider adding slow checks to excluded list in `test:fast`