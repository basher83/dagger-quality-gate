"""Python code quality checks (ruff, black, mypy, Ty)."""

from dagger import Client, Directory
from config import CheckConfig
from main import CheckResult
from .base import prepare_python_container_with_uv
from output_parser import parse_output


async def run_python_check(
    client: Client, source: Directory, check_name: str, config: CheckConfig
) -> CheckResult:
    """Run Python quality checks."""
    try:
        # Create base Python container
        if not config.container_image:
            raise ValueError(f"No container image specified for {check_name}")

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
        elif check_name == "black":
            return await _run_black(container, config)
        else:
            return CheckResult(
                check_name, False, error=f"Unknown Python check: {check_name}"
            )

    except Exception as e:
        return CheckResult(
            check_name, False, error=f"Failed to run {check_name}: {str(e)}"
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
            
            # Parse output for structured data
            parsed = parse_output("ruff", output)
            if parsed:
                return CheckResult(
                    "ruff",
                    True,
                    output=output,
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult("ruff", True, output=output)
        except Exception:
            # Get stderr for error details
            stderr = await container.with_exec(cmd).stderr()
            stdout = await container.with_exec(cmd).stdout()
            
            # Parse output for structured data
            parsed = parse_output("ruff", stdout, stderr)
            if parsed:
                return CheckResult(
                    "ruff",
                    False,
                    output=stdout,
                    error=stderr or "Ruff check failed",
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult(
                    "ruff", False, output=stdout, error=stderr or "Ruff check failed"
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
            
            # Parse output for structured data
            parsed = parse_output("mypy", output)
            if parsed:
                return CheckResult(
                    "mypy",
                    True,
                    output=output,
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult("mypy", True, output=output)
        except Exception:
            # Get output for error details
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()
            
            # Parse output for structured data
            parsed = parse_output("mypy", stdout, stderr)
            if parsed:
                return CheckResult(
                    "mypy",
                    False,
                    output=stdout,
                    error=stderr or stdout or "MyPy check failed",
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult(
                    "mypy",
                    False,
                    output=stdout,
                    error=stderr or stdout or "MyPy check failed",
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
            
            # Parse output for structured data
            parsed = parse_output("ty", output)
            if parsed:
                return CheckResult(
                    "ty",
                    True,
                    output=output,
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult("ty", True, output=output)
        except Exception:
            # Get output for error details
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()
            
            # Parse output for structured data
            parsed = parse_output("ty", stdout, stderr)
            if parsed:
                return CheckResult(
                    "ty",
                    False,
                    output=stdout,
                    error=stderr or stdout or "Ty check failed",
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult(
                    "ty", False, output=stdout, error=stderr or stdout or "Ty check failed"
                )

    except Exception as e:
        return CheckResult("ty", False, error=str(e))


async def _run_black(container, config: CheckConfig) -> CheckResult:
    """Run Black formatter in check mode."""
    try:
        # Prepare container with uv and install black
        container = prepare_python_container_with_uv(container)
        container = container.with_exec(["uv", "pip", "install", "--system", "black"])

        # Build command - run in check mode to verify formatting
        cmd = ["black", "--check", "--diff", "."]
        cmd.extend(config.additional_args)

        # Run Black
        result = await container.with_exec(cmd).sync()

        try:
            output = await result.stdout()
            await result.exit_code()  # Will raise if non-zero
            
            # Parse output for structured data
            parsed = parse_output("black", output)
            if parsed:
                return CheckResult(
                    "black",
                    True,
                    output=output or "All files are properly formatted",
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult(
                    "black", True, output=output or "All files are properly formatted"
                )
        except Exception:
            # Get output for error details
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()
            
            # Parse output for structured data
            parsed = parse_output("black", stdout, stderr)
            if parsed:
                return CheckResult(
                    "black",
                    False,
                    output=stdout,
                    error=stderr or stdout or "Black formatting check failed",
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult(
                    "black",
                    False,
                    output=stdout,
                    error=stderr or stdout or "Black formatting check failed",
                )

    except Exception as e:
        return CheckResult("black", False, error=str(e))
