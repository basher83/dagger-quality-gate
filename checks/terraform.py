"""Terraform code quality checks (terraform fmt, tflint)."""

from dagger import Client, Directory
from config import CheckConfig
from main import CheckResult
from output_parser import parse_output


async def run_terraform_check(
    client: Client, source: Directory, check_name: str, config: CheckConfig
) -> CheckResult:
    """Run Terraform quality checks."""
    try:
        if check_name == "terraform":
            return await _run_terraform_fmt(client, source, config)
        elif check_name == "tflint":
            return await _run_tflint(client, source, config)
        else:
            return CheckResult(
                check_name, False, error=f"Unknown Terraform check: {check_name}"
            )

    except Exception as e:
        return CheckResult(
            check_name, False, error=f"Failed to run {check_name}: {str(e)}"
        )


async def _run_terraform_fmt(
    client: Client, source: Directory, config: CheckConfig
) -> CheckResult:
    """Run terraform fmt check."""
    try:
        # Create container with terraform
        if not config.container_image:
            raise ValueError("No container image specified for terraform")

        container = (
            client.container()
            .from_(config.container_image)
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
        )

        # Build command - check formatting
        cmd = ["terraform", "fmt", "-check", "-recursive"]
        cmd.extend(config.additional_args)

        # Run terraform fmt
        result = await container.with_exec(cmd).sync()

        try:
            output = await result.stdout()
            await result.exit_code()  # Will raise if non-zero
            parsed = parse_output("terraform", output)
            if parsed:
                return CheckResult(
                    "terraform",
                    True,
                    output=output or "All Terraform files properly formatted",
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult(
                    "terraform",
                    True,
                    output=output or "All Terraform files properly formatted",
                )
        except Exception:
            # Get list of files that need formatting
            list_cmd = ["terraform", "fmt", "-check", "-recursive", "-list=true"]
            stdout = await container.with_exec(list_cmd).stdout()

            if stdout:
                error_msg = f"The following files need formatting:\n{stdout}"
            else:
                error_msg = "Terraform formatting check failed"

            parsed = parse_output("terraform", stdout)
            if parsed:
                return CheckResult(
                    "terraform",
                    False,
                    output=stdout,
                    error=error_msg,
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult("terraform", False, output=stdout, error=error_msg)

    except Exception as e:
        return CheckResult("terraform", False, error=str(e))


async def _run_tflint(
    client: Client, source: Directory, config: CheckConfig
) -> CheckResult:
    """Run tflint linter."""
    try:
        # Create container with tflint
        if not config.container_image:
            raise ValueError("No container image specified for tflint")

        container = (
            client.container()
            .from_(config.container_image)
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
        )

        # Initialize tflint (download plugins)
        init_result = await container.with_exec(["tflint", "--init"]).sync()

        try:
            await init_result.exit_code()
        except Exception:
            # Initialization might fail if no config, that's ok
            pass

        # Build command
        cmd = ["tflint"]
        cmd.extend(config.additional_args)

        # Run tflint
        result = await container.with_exec(cmd).sync()

        try:
            output = await result.stdout()
            await result.exit_code()  # Will raise if non-zero
            parsed = parse_output("tflint", output)
            if parsed:
                return CheckResult(
                    "tflint",
                    True,
                    output=output or "No issues found",
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult("tflint", True, output=output or "No issues found")
        except Exception:
            # Get output for error details
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()

            error_output = stderr or stdout or "TFLint found issues"

            parsed = parse_output("tflint", stdout, stderr)
            if parsed:
                return CheckResult(
                    "tflint",
                    False,
                    output=stdout,
                    error=error_output,
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult("tflint", False, output=stdout, error=error_output)

    except Exception as e:
        return CheckResult("tflint", False, error=str(e))
