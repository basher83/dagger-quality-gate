"""Markdown linting check using markdownlint."""

from dagger import Client, Directory
from config import CheckConfig
from main import CheckResult
from output_parser import parse_output


async def run_markdown_check(
    client: Client, source: Directory, config: CheckConfig
) -> CheckResult:
    """Run markdownlint on markdown files."""
    try:
        # Create container with markdownlint
        if not config.container_image:
            raise ValueError("No container image specified for markdown")

        container = (
            client.container()
            .from_(config.container_image)
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
        )

        # Build command
        cmd = ["markdownlint-cli2", "**/*.md"]
        cmd.extend(config.additional_args)

        # Run markdownlint
        result = await container.with_exec(cmd).sync()

        # Check exit code (markdownlint returns 0 on success, 1 on lint errors)
        try:
            output = await result.stdout()
            exit_code = await result.exit_code()

            if exit_code == 0:
                parsed = parse_output("markdown", output)
                if parsed:
                    return CheckResult(
                        "markdown",
                        True,
                        output=output,
                        issues=parsed.issues,
                        fix_command=parsed.fix_command,
                        summary=parsed.summary,
                    )
                else:
                    return CheckResult("markdown", True, output=output)
            else:
                # Get stderr for error details
                stderr = await result.stderr()
                parsed = parse_output("markdown", output, stderr)
                if parsed:
                    return CheckResult(
                        "markdown",
                        False,
                        output=output,
                        error=stderr or "Markdown linting failed",
                        issues=parsed.issues,
                        fix_command=parsed.fix_command,
                        summary=parsed.summary,
                    )
                else:
                    return CheckResult(
                        "markdown",
                        False,
                        output=output,
                        error=stderr or "Markdown linting failed",
                    )
        except Exception:
            # If exit code is non-zero, Dagger will raise an exception
            stdout = await container.with_exec(cmd).stdout()
            stderr = await container.with_exec(cmd).stderr()
            parsed = parse_output("markdown", stdout, stderr)
            if parsed:
                return CheckResult(
                    "markdown",
                    False,
                    output=stdout,
                    error=stderr or "Markdown linting failed",
                    issues=parsed.issues,
                    fix_command=parsed.fix_command,
                    summary=parsed.summary,
                )
            else:
                return CheckResult(
                    "markdown", False, error=stderr or "Markdown linting failed"
                )

    except Exception as e:
        return CheckResult(
            "markdown", False, error=f"Failed to run markdownlint: {str(e)}"
        )
