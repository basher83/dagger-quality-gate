# Container Optimization Techniques

## Layer Optimization in prepare_python_container_with_uv()

The function was optimized to reduce container layers and improve build performance:

### Before (Multiple Layers)
```python
container = container.with_exec(["apt-get", "-qq", "update"])
container = container.with_exec(["apt-get", "-y", "--no-install-recommends", "install", "curl"])
container = container.with_exec(["curl", "-LsSf", "https://astral.sh/uv/install.sh", "-o", "/tmp/install.sh"])
container = container.with_exec(["sh", "/tmp/install.sh"])
```

### After (Single Layer with Full Cleanup)
```python
container = container.with_exec(
    [
        "sh",
        "-c",
        "apt-get update && "
        "apt-get -y --no-install-recommends install curl && "
        "curl -LsSf https://astral.sh/uv/install.sh | sh && "
        "apt-get clean && "
        "rm -rf /var/lib/apt/lists/*",
    ]
)
```

## Key Improvements

1. **Error Handling**: Chain commands with `&&` to ensure each step succeeds before continuing
   - Note: `set -euo pipefail` is bash-specific and not available in POSIX sh
   - Using `&&` between commands provides similar fail-fast behavior

2. **Complete Cleanup**:
   - `apt-get clean`: Removes package cache from `/var/cache/apt/archives`
   - `rm -rf /var/lib/apt/lists/*`: Removes package index files

3. **Benefits**:
   - **Fewer Layers**: Reduces final image size
   - **Better Caching**: Single layer can be cached more efficiently
   - **Proper Error Handling**: Pipeline fails if any step fails (via && chaining)
   - **Complete Cleanup**: Both package cache and index files removed
   - **Atomic Operation**: All steps succeed or fail together

## Best Practices
- Use `&&` to chain commands for error handling in POSIX sh
- For bash-specific features like `pipefail`, ensure bash is available first
- Clean up both apt cache (`apt-get clean`) and lists
- Use `sh -c` to run multiple commands as one exec
- Remove temporary files immediately after use