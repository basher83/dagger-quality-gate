#!/usr/bin/env python3
"""Main Dagger quality gate pipeline."""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List

import anyio
import dagger
from dagger import Client, Directory
from rich.console import Console
from rich.table import Table

from config import load_config, get_enabled_checks, PipelineConfig, CheckConfig


console = Console()


class CheckResult:
    """Result of a quality check."""

    def __init__(self, name: str, passed: bool, output: str = "", error: str = ""):
        self.name = name
        self.passed = passed
        self.output = output
        self.error = error


class QualityGatePipeline:
    """Main pipeline orchestrator."""

    def __init__(self, config: PipelineConfig, source_dir: str = "."):
        self.config = config
        self.source_dir = Path(source_dir).resolve()
        self.results: List[CheckResult] = []

    async def run(self) -> int:
        """Run the quality gate pipeline."""
        console.print("[bold blue]🚀 Starting Dagger Quality Gate Pipeline[/bold blue]")

        async with dagger.Connection() as client:
            # Mount source directory
            source = client.host().directory(str(self.source_dir))

            # Get enabled checks
            enabled_checks = get_enabled_checks(self.config)

            if not enabled_checks:
                console.print(
                    "[yellow]⚠️  No checks enabled. Set ENABLE_<CHECK>=true to enable checks.[/yellow]"
                )
                return 0

            console.print(f"[green]✓[/green] Found {len(enabled_checks)} enabled checks")

            # Run checks
            if self.config.parallel:
                results = await self._run_parallel(client, source, enabled_checks)
            else:
                results = await self._run_sequential(client, source, enabled_checks)

            # Display results
            self._display_results(results)

            # Determine exit code
            failed_checks = [r for r in results if not r.passed]
            if failed_checks:
                console.print(f"\n[red]❌ {len(failed_checks)} check(s) failed[/red]")
                return 1
            else:
                console.print("\n[green]✅ All checks passed![/green]")
                return 0

    async def _run_parallel(
        self, client: Client, source: Directory, checks: Dict[str, CheckConfig]
    ) -> List[CheckResult]:
        """Run checks in parallel."""
        console.print("[dim]Running checks in parallel...[/dim]")

        tasks = []
        for check_name, check_config in checks.items():
            task = self._run_check(client, source, check_name, check_config)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed results
        final_results = []
        for i, result in enumerate(results):
            check_name = list(checks.keys())[i]
            if isinstance(result, Exception):
                final_results.append(CheckResult(check_name, False, error=str(result)))
            else:
                final_results.append(result)

        return final_results

    async def _run_sequential(
        self, client: Client, source: Directory, checks: Dict[str, CheckConfig]
    ) -> List[CheckResult]:
        """Run checks sequentially."""
        console.print("[dim]Running checks sequentially...[/dim]")

        results = []
        for check_name, check_config in checks.items():
            try:
                result = await self._run_check(client, source, check_name, check_config)
                results.append(result)

                if not result.passed and self.config.fail_fast:
                    console.print(f"[red]Failed fast on {check_name}[/red]")
                    break
            except Exception as e:
                result = CheckResult(check_name, False, error=str(e))
                results.append(result)

                if self.config.fail_fast:
                    break

        return results

    async def _run_check(
        self, client: Client, source: Directory, check_name: str, check_config: CheckConfig
    ) -> CheckResult:
        """Run a single check."""
        # Don't use status in parallel mode to avoid conflicts
        if not self.config.parallel:
            console.print(f"[dim]Running {check_name}...[/dim]")

        # Import the appropriate check module
        try:
            if check_name == "markdown":
                from checks.markdown import run_markdown_check

                return await run_markdown_check(client, source, check_config)

            elif check_name in ["ruff", "mypy", "ty", "black"]:
                from checks.python import run_python_check

                return await run_python_check(client, source, check_name, check_config)

            elif check_name in ["bandit", "semgrep", "safety"]:
                from checks.security import run_security_check

                return await run_security_check(client, source, check_name, check_config)

            elif check_name in ["terraform", "tflint"]:
                from checks.terraform import run_terraform_check

                return await run_terraform_check(client, source, check_name, check_config)

            elif check_name == "gitleaks":
                from checks.secrets import run_gitleaks_check

                return await run_gitleaks_check(client, source, check_config)

            else:
                return CheckResult(check_name, False, error=f"Unknown check: {check_name}")

        except Exception as e:
            return CheckResult(check_name, False, error=f"Error running check: {str(e)}")

    def _display_results(self, results: List[CheckResult]):
        """Display check results in a table."""
        table = Table(title="Quality Gate Results")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details")

        for result in results:
            status = "[green]✓ PASS[/green]" if result.passed else "[red]✗ FAIL[/red]"
            details = result.error if result.error else "OK"

            if self.config.verbose and result.output:
                details = result.output[:100] + "..." if len(result.output) > 100 else result.output

            table.add_row(result.name, status, details)

        console.print("\n", table)


async def main():
    """Main entry point."""
    # Load configuration
    config = load_config()

    # Get source directory from command line or use current directory
    source_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    # Run pipeline
    pipeline = QualityGatePipeline(config, source_dir)
    exit_code = await pipeline.run()

    sys.exit(exit_code)


if __name__ == "__main__":
    anyio.run(main)
