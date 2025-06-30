#!/usr/bin/env python3
"""Main Dagger quality gate pipeline."""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional

import anyio
import dagger
from dagger import Client, Directory
from rich.console import Console
from rich.table import Table

from config import load_config, get_enabled_checks, PipelineConfig, CheckConfig
from output_parser import parse_output, Issue, IssueSeverity


console = Console()


class CheckResult:
    """Result of a quality check."""

    def __init__(
        self,
        name: str,
        passed: bool,
        output: str = "",
        error: str = "",
        issues: Optional[List[Issue]] = None,
        fix_command: Optional[str] = None,
        summary: Optional[str] = None,
    ):
        self.name = name
        self.passed = passed
        self.output = output
        self.error = error
        self.issues = issues or []
        self.fix_command = fix_command
        self.summary = summary


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

            console.print(
                f"[green]✓[/green] Found {len(enabled_checks)} enabled checks"
            )

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
                # Summary is displayed in _display_results
                return 1
            else:
                # Success message is displayed in _display_results
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
        final_results: List[CheckResult] = []
        for i, result in enumerate(results):
            check_name = list(checks.keys())[i]
            if isinstance(result, Exception):
                final_results.append(CheckResult(check_name, False, error=str(result)))
            else:
                # MyPy should understand this is CheckResult from return_exceptions=True
                final_results.append(result)  # type: ignore[arg-type]

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
        self,
        client: Client,
        source: Directory,
        check_name: str,
        check_config: CheckConfig,
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

                return await run_security_check(
                    client, source, check_name, check_config
                )

            elif check_name in ["terraform", "tflint"]:
                from checks.terraform import run_terraform_check

                return await run_terraform_check(
                    client, source, check_name, check_config
                )

            elif check_name == "gitleaks":
                from checks.secrets import run_gitleaks_check

                return await run_gitleaks_check(client, source, check_config)

            else:
                return CheckResult(
                    check_name, False, error=f"Unknown check: {check_name}"
                )

        except Exception as e:
            return CheckResult(
                check_name, False, error=f"Error running check: {str(e)}"
            )

    def _display_results(self, results: List[CheckResult]):
        """Display check results with enhanced formatting."""
        # Count issues by severity
        total_issues = 0
        errors = 0
        warnings = 0
        info = 0
        fixable_issues = 0
        files_with_issues = set()
        
        for result in results:
            if result.issues:
                for issue in result.issues:
                    total_issues += 1
                    files_with_issues.add(issue.file_path)
                    if issue.severity.value == "error":
                        errors += 1
                    elif issue.severity.value == "warning":
                        warnings += 1
                    else:
                        info += 1
            if result.fix_command:
                fixable_issues += 1
        
        # Display summary header
        if total_issues > 0:
            console.print(f"\n[bold red]❌ Quality Gate Failed: {total_issues} issues found[/bold red]")
            console.print(f"\n[bold]📊 Summary:[/bold]")
            if errors > 0:
                console.print(f"  • {errors} error{'s' if errors != 1 else ''}")
            if warnings > 0:
                console.print(f"  • {warnings} warning{'s' if warnings != 1 else ''}")
            if info > 0:
                console.print(f"  • {info} style/info issue{'s' if info != 1 else ''}")
            if fixable_issues > 0:
                console.print(f"  • {fixable_issues} auto-fixable")
            console.print(f"  • Issues in {len(files_with_issues)} file{'s' if len(files_with_issues) != 1 else ''}")
        else:
            console.print("\n[bold green]✅ All checks passed![/bold green]")
        
        # Display detailed results for each check
        for result in results:
            if not result.passed or (self.config.verbose and result.issues):
                console.print(f"\n[bold]🔍 {result.name.title()}:[/bold]", end="")
                
                if result.summary:
                    console.print(f" {result.summary}")
                elif result.passed:
                    console.print(" [green]Passed[/green]")
                else:
                    console.print(" [red]Failed[/red]")
                
                # Show issues grouped by file
                if result.issues and (not result.passed or self.config.verbose):
                    files_dict = {}
                    for issue in result.issues:
                        if issue.file_path not in files_dict:
                            files_dict[issue.file_path] = []
                        files_dict[issue.file_path].append(issue)
                    
                    for file_path, file_issues in files_dict.items():
                        console.print(f"\n  [cyan]📁 {file_path}[/cyan]")
                        for issue in file_issues[:5]:  # Limit to 5 issues per file
                            location = f"Line {issue.line_number}" if issue.line_number else "File"
                            if issue.column_number:
                                location += f":{issue.column_number}"
                            
                            severity_color = {
                                "error": "red",
                                "warning": "yellow",
                                "info": "blue",
                                "style": "magenta"
                            }.get(issue.severity.value, "white")
                            
                            console.print(f"    [{severity_color}]{location}[/{severity_color}]: {issue.message}")
                            if issue.rule_id:
                                console.print(f"      Rule: {issue.rule_id}", style="dim")
                        
                        if len(file_issues) > 5:
                            console.print(f"    ... and {len(file_issues) - 5} more issues", style="dim")
                
                # Show fix command if available
                if result.fix_command:
                    console.print(f"\n  💡 Run `{result.fix_command}` to automatically fix these issues")
            
            elif result.passed and not self.config.verbose:
                # Just show a simple checkmark for passed checks in non-verbose mode
                continue
        
        # Show available fix commands at the end
        fix_commands = [r.fix_command for r in results if r.fix_command and not r.passed]
        if fix_commands:
            console.print("\n[bold]To automatically fix formatting issues, run:[/bold]")
            for cmd in set(fix_commands):
                console.print(f"  {cmd}")
        
        # Classic table view as fallback or in verbose mode
        if self.config.verbose:
            console.print("\n[dim]Classic view:[/dim]")
            table = Table(title="Quality Gate Results")
            table.add_column("Check", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Summary")
            
            for result in results:
                status = "[green]✓ PASS[/green]" if result.passed else "[red]✗ FAIL[/red]"
                summary = result.summary or result.error or "OK"
                table.add_row(result.name, status, summary)
            
            console.print(table)


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


def run():
    """Synchronous entry point for console script."""
    anyio.run(main)


if __name__ == "__main__":
    run()
