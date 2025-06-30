"""Markdown linting check using markdownlint."""

from dagger import Client, Directory
from config import CheckConfig
from main import CheckResult


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
                return CheckResult("markdown", True, output=output)
            else:
                # Get stderr for error details
                stderr = await result.stderr()
                return CheckResult(
                    "markdown",
                    False,
                    output=output,
                    error=stderr or "Markdown linting failed",
                )
        except Exception:
            # If exit code is non-zero, Dagger will raise an exception
            stderr = await container.with_exec(cmd).stderr()
            return CheckResult(
                "markdown", False, error=stderr or "Markdown linting failed"
            )

    except Exception as e:
        return CheckResult(
            "markdown", False, error=f"Failed to run markdownlint: {str(e)}"
        )
