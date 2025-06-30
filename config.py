"""Configuration management for Dagger quality gate pipeline."""

import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CheckConfig(BaseModel):
    """Configuration for an individual check."""

    enabled: bool = True
    container_image: Optional[str] = None
    additional_args: List[str] = Field(default_factory=list)


class PipelineConfig(BaseModel):
    """Main configuration for the quality gate pipeline."""

    # General settings
    fail_fast: bool = Field(default=True, description="Stop pipeline on first failure")

    parallel: bool = Field(default=True, description="Run checks in parallel")

    verbose: bool = Field(default=False, description="Enable verbose output")

    # Check configurations
    markdown: CheckConfig = Field(
        default_factory=lambda: CheckConfig(
            container_image="davidanson/markdownlint-cli2:latest"
        )
    )

    ruff: CheckConfig = Field(
        default_factory=lambda: CheckConfig(container_image="python:3.11-slim")
    )

    mypy: CheckConfig = Field(
        default_factory=lambda: CheckConfig(container_image="python:3.11-slim")
    )

    ty: CheckConfig = Field(
        default_factory=lambda: CheckConfig(container_image="python:3.11-slim")
    )

    black: CheckConfig = Field(
        default_factory=lambda: CheckConfig(container_image="python:3.11-slim")
    )

    bandit: CheckConfig = Field(
        default_factory=lambda: CheckConfig(container_image="python:3.11-slim")
    )

    semgrep: CheckConfig = Field(
        default_factory=lambda: CheckConfig(
            container_image="returntocorp/semgrep:latest"
        )
    )

    safety: CheckConfig = Field(
        default_factory=lambda: CheckConfig(container_image="python:3.11-slim")
    )

    terraform: CheckConfig = Field(
        default_factory=lambda: CheckConfig(
            container_image="hashicorp/terraform:latest"
        )
    )

    tflint: CheckConfig = Field(
        default_factory=lambda: CheckConfig(
            container_image="ghcr.io/terraform-linters/tflint:latest"
        )
    )

    gitleaks: CheckConfig = Field(
        default_factory=lambda: CheckConfig(
            container_image="zricethezav/gitleaks:latest"
        )
    )


def str_to_bool(value: str) -> bool:
    """Convert string to boolean."""
    return value.lower() in ("true", "1", "yes", "on")


def load_config() -> PipelineConfig:
    """Load configuration from environment variables."""
    # Start with default config
    default_config = PipelineConfig()
    config_dict: Dict[str, Any] = {}

    # General settings
    if val := os.getenv("FAIL_FAST"):
        config_dict["fail_fast"] = str_to_bool(val)

    if val := os.getenv("PARALLEL"):
        config_dict["parallel"] = str_to_bool(val)

    if val := os.getenv("VERBOSE"):
        config_dict["verbose"] = str_to_bool(val)

    # Check-specific settings
    checks = [
        "markdown",
        "ruff",
        "mypy",
        "ty",
        "black",
        "bandit",
        "semgrep",
        "safety",
        "terraform",
        "tflint",
        "gitleaks",
    ]

    for check in checks:
        # Get the default check config
        default_check_config = getattr(default_config, check)
        check_config = {
            "enabled": default_check_config.enabled,
            "container_image": default_check_config.container_image,
            "additional_args": default_check_config.additional_args.copy(),
        }

        # Override with environment variables
        if val := os.getenv(f"ENABLE_{check.upper()}"):
            check_config["enabled"] = str_to_bool(val)

        # Custom container image
        if val := os.getenv(f"{check.upper()}_IMAGE"):
            check_config["container_image"] = val

        # Additional arguments
        if val := os.getenv(f"{check.upper()}_ARGS"):
            check_config["additional_args"] = val.split()

        config_dict[check] = CheckConfig(**check_config)

    return PipelineConfig(**config_dict)


def get_enabled_checks(config: PipelineConfig) -> Dict[str, CheckConfig]:
    """Get dictionary of enabled checks."""
    enabled = {}

    for check_name in [
        "markdown",
        "ruff",
        "mypy",
        "ty",
        "black",
        "bandit",
        "semgrep",
        "safety",
        "terraform",
        "tflint",
        "gitleaks",
    ]:
        check_config = getattr(config, check_name)
        if check_config.enabled:
            enabled[check_name] = check_config

    return enabled
