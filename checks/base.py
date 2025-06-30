"""Base utilities for check modules."""

from dagger import Container


def prepare_python_container_with_uv(container: Container) -> Container:
    """Prepare a Python container with uv installed and configured."""
    return (
        container.with_exec(
            [
                "sh",
                "-c",
                "set -euo pipefail && "
                "apt-get -qq update && "
                "apt-get -y --no-install-recommends install curl && "
                "curl -LsSf https://astral.sh/uv/install.sh | sh && "
                "apt-get clean && "
                "rm -rf /var/lib/apt/lists/*",
            ]
        )
        # Set PATH properly to include uv location
        .with_env_variable(
            "PATH", "/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        )
    )


def get_uv_tool_path(tool_name: str) -> str:
    """Get the full path to a uv-installed tool."""
    return f"/root/.local/share/uv/tools/{tool_name}/bin/{tool_name}"
