"""Python code quality checks (ruff, mypy, Ty)."""

from dagger import Client, Directory
from config import CheckConfig
from main import CheckResult
from .base import prepare_python_container_with_uv, get_uv_tool_path


async def run_python_check(
    client: Client,
    source: Directory,
    check_name: str,
    config: CheckConfig
) -> CheckResult:
    """Run Python quality checks."""
    try:
        # Create base Python container
        container = (
            client.container()
            .from_(config.container_image)
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
        )
        
        # Install the appropriate tool and run it
        if check_name == "ruff":
            return await _run_ruff(container, config)
        elif check_name == "mypy":
            return await _run_mypy(container, config)
        elif check_name == "ty":
            return await _run_ty(container, config)
        else:
            return CheckResult(
                check_name,
                False,
                error=f"Unknown Python check: {check_name}"
            )
    
    except Exception as e:
        return CheckResult(
            check_name,
            False,
            error=f"Failed to run {check_name}: {str(e)}"
        )


async def _run_ruff(container, config: CheckConfig) -> CheckResult:
    """Run ruff linter."""
    try:
        # Prepare container with uv and install ruff
        container = prepare_python_container_with_uv(container)
        container = container.with_exec(["uv", "tool", "install", "ruff"])
        
        # Build command - uv tools are installed in a specific location
        cmd = ["/root/.local/share/uv/tools/ruff/bin/ruff", "check", "."]
        cmd.extend(config.additional_args)
        
        # Run ruff
        result = await container.with_exec(cmd).sync()
        
        try:
            output = await result.stdout()
            await result.exit_code()  # Will raise if non-zero
            return CheckResult("ruff", True, output=output)
        except Exception:
            # Get stderr for error details
            stderr = await container.with_exec(cmd).stderr()
            stdout = await container.with_exec(cmd).stdout()
            return CheckResult(
                "ruff",
                False,
                output=stdout,
                error=stderr or "Ruff check failed"
            )
    
    except Exception as e:
        return CheckResult("ruff", False, error=str(e))


async def _run_mypy(container, config: CheckConfig) -> CheckResult:
    """Run mypy type checker."""
    try:
        # Prepare container with uv and install mypy
        container = prepare_python_container_with_uv(container)
        container = container.with_exec(["uv", "pip", "install", "--system", "mypy"])
        
        # Build command
        cmd = ["mypy", "."]
        cmd.extend(config.additional_args)
        
        # Run mypy
        result = await container.with_exec(cmd).sync()
        
        try:
            output = await result.stdout()
            await result.exit_code()  # Will raise if non-zero
            return CheckResult("mypy", True, output=output)
        except Exception:
            # Get output for error details
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()
            return CheckResult(
                "mypy",
                False,
                output=stdout,
                error=stderr or stdout or "MyPy check failed"
            )
    
    except Exception as e:
        return CheckResult("mypy", False, error=str(e))


async def _run_ty(container, config: CheckConfig) -> CheckResult:
    """Run Ty type checker."""
    try:
        # Prepare container with uv and install ty
        container = prepare_python_container_with_uv(container)
        container = container.with_exec(["uv", "tool", "install", "ty"])
        
        # Build command - uv tools are installed in a specific location
        cmd = ["/root/.local/share/uv/tools/ty/bin/ty", "check", "."]
        cmd.extend(config.additional_args)
        
        # Run Ty
        result = await container.with_exec(cmd).sync()
        
        try:
            output = await result.stdout()
            await result.exit_code()  # Will raise if non-zero
            return CheckResult("ty", True, output=output)
        except Exception:
            # Get output for error details
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()
            return CheckResult(
                "ty",
                False,
                output=stdout,
                error=stderr or stdout or "Ty check failed"
            )
    
    except Exception as e:
        return CheckResult("ty", False, error=str(e))