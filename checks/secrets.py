"""Secrets scanning check using Gitleaks."""

from dagger import Client, Directory
from config import CheckConfig
from main import CheckResult
from output_parser import parse_output


async def run_gitleaks_check(
    client: Client, source: Directory, config: CheckConfig
) -> CheckResult:
    """Run Gitleaks secrets scanner."""
    try:
        # Create container with gitleaks
        if not config.container_image:
            raise ValueError("No container image specified for gitleaks")

        container = (
            client.container()
            .from_(config.container_image)
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
        )

        # Build command
        cmd = ["gitleaks", "detect", "--source", ".", "--verbose"]

        # Add config file if it exists
        try:
            await container.with_exec(["test", "-f", ".gitleaks.toml"]).sync()
            cmd.extend(["--config", ".gitleaks.toml"])
        except Exception:
            # No custom config, use defaults
            pass

        # Check for .gitleaksignore file
        try:
            await container.with_exec(["test", "-f", ".gitleaksignore"]).sync()
            cmd.extend(["--baseline-path", ".gitleaksignore"])
        except Exception:
            # No ignore file
            pass

        cmd.extend(config.additional_args)

        # Run gitleaks
        result = await container.with_exec(cmd).sync()

        try:
            output = await result.stdout()
            await result.exit_code()  # Will raise if non-zero
            parsed = parse_output("gitleaks", output)
            if parsed:
                return CheckResult(
                    "gitleaks",
                    True,
                    output=output or "No secrets found",
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult("gitleaks", True, output=output or "No secrets found")
        except Exception:
            # Get output for error details
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()

            # Gitleaks outputs to stderr on findings
            error_output = stderr or stdout or "Gitleaks found secrets"

            parsed = parse_output("gitleaks", stdout, stderr)
            if parsed:
                return CheckResult(
                    "gitleaks",
                    False,
                    output=stdout,
                    error=error_output,
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult("gitleaks", False, output=stdout, error=error_output)

    except Exception as e:
        return CheckResult("gitleaks", False, error=str(e))
