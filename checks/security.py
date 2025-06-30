"""Security scanning checks (Bandit, Semgrep, Safety)."""

from dagger import Client, Directory
from config import CheckConfig
from main import CheckResult
from .base import prepare_python_container_with_uv, get_uv_tool_path


async def run_security_check(
    client: Client,
    source: Directory,
    check_name: str,
    config: CheckConfig
) -> CheckResult:
    """Run security scanning checks."""
    try:
        if check_name == "bandit":
            return await _run_bandit(client, source, config)
        elif check_name == "semgrep":
            return await _run_semgrep(client, source, config)
        elif check_name == "safety":
            return await _run_safety(client, source, config)
        else:
            return CheckResult(
                check_name,
                False,
                error=f"Unknown security check: {check_name}"
            )
    
    except Exception as e:
        return CheckResult(
            check_name,
            False,
            error=f"Failed to run {check_name}: {str(e)}"
        )


async def _run_bandit(client: Client, source: Directory, config: CheckConfig) -> CheckResult:
    """Run Bandit security scanner for Python."""
    try:
        # Create container and install bandit with uv
        container = (
            client.container()
            .from_(config.container_image)
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
        )
        container = prepare_python_container_with_uv(container)
        container = container.with_exec(["uv", "pip", "install", "--system", "bandit[toml]"])
        
        # Build command
        cmd = ["bandit", "-r", "."]
        cmd.extend(config.additional_args)
        
        # Run bandit
        result = await container.with_exec(cmd).sync()
        
        try:
            output = await result.stdout()
            await result.exit_code()  # Will raise if non-zero
            return CheckResult("bandit", True, output=output)
        except Exception:
            # Get output for error details
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()
            return CheckResult(
                "bandit",
                False,
                output=stdout,
                error=stderr or "Bandit found security issues"
            )
    
    except Exception as e:
        return CheckResult("bandit", False, error=str(e))


async def _run_semgrep(client: Client, source: Directory, config: CheckConfig) -> CheckResult:
    """Run Semgrep security scanner."""
    try:
        # Use semgrep container image
        container = (
            client.container()
            .from_(config.container_image)
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
        )
        
        # Build command - use auto config by default
        cmd = ["semgrep", "--config=auto"]
        cmd.extend(config.additional_args)
        
        # Run semgrep
        result = await container.with_exec(cmd).sync()
        
        try:
            output = await result.stdout()
            await result.exit_code()  # Will raise if non-zero
            return CheckResult("semgrep", True, output=output)
        except Exception:
            # Get output for error details
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()
            return CheckResult(
                "semgrep",
                False,
                output=stdout,
                error=stderr or "Semgrep found security issues"
            )
    
    except Exception as e:
        return CheckResult("semgrep", False, error=str(e))


async def _run_safety(client: Client, source: Directory, config: CheckConfig) -> CheckResult:
    """Run Safety vulnerability scanner for Python dependencies."""
    try:
        # Create container and install safety with uv
        container = (
            client.container()
            .from_(config.container_image)
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
        )
        container = prepare_python_container_with_uv(container)
        container = container.with_exec(["uv", "pip", "install", "--system", "safety"])
        
        # Build command - use new scan command
        cmd = ["safety", "scan"]
        
        # Check if requirements.txt exists
        try:
            await container.with_exec(["test", "-f", "requirements.txt"]).sync()
            # For scan command, we don't need --file flag
            pass
        except Exception:
            # No requirements.txt, safety will scan the current directory
            pass
        
        cmd.extend(config.additional_args)
        
        # Run safety
        result = await container.with_exec(cmd).sync()
        
        try:
            output = await result.stdout()
            await result.exit_code()  # Will raise if non-zero
            return CheckResult("safety", True, output=output)
        except Exception:
            # Get output for error details
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()
            return CheckResult(
                "safety",
                False,
                output=stdout,
                error=stderr or stdout or "Safety found vulnerabilities"
            )
    
    except Exception as e:
        return CheckResult("safety", False, error=str(e))