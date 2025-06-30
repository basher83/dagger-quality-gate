"""Output parsers for various quality check tools."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from enum import Enum


class IssueSeverity(Enum):
    """Severity levels for issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    STYLE = "style"


@dataclass
class Issue:
    """Represents a single issue found by a quality check tool."""

    file_path: str
    line_number: Optional[int]
    column_number: Optional[int]
    severity: IssueSeverity
    rule_id: Optional[str]
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None


@dataclass
class ParsedOutput:
    """Parsed output from a quality check tool."""

    tool_name: str
    issues: List[Issue]
    summary: str
    total_files_checked: Optional[int] = None
    fix_command: Optional[str] = None
    raw_output: Optional[str] = None


class BaseParser(ABC):
    """Base class for tool output parsers."""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name

    @abstractmethod
    def parse(self, output: str, error: str = "") -> ParsedOutput:
        """Parse tool output and return structured data."""
        pass

    def _extract_file_info(self, text: str) -> Tuple[str, Optional[int], Optional[int]]:
        """Extract file path, line, and column from common patterns."""
        # Pattern: file.py:line:column
        match = re.match(r"^([^:]+):(\d+)(?::(\d+))?", text)
        if match:
            return (
                match.group(1),
                int(match.group(2)) if match.group(2) else None,
                int(match.group(3)) if match.group(3) else None,
            )
        return text, None, None


class BlackParser(BaseParser):
    """Parser for Black formatter output."""

    def __init__(self):
        super().__init__("black")

    def parse(self, output: str, error: str = "") -> ParsedOutput:
        issues = []

        # Black outputs diff when files need formatting
        if "would reformat" in output or "reformatted" in output:
            # Extract files that need formatting
            for line in output.splitlines():
                if "would reformat" in line:
                    file_path = line.split("would reformat")[1].strip()
                    issues.append(
                        Issue(
                            file_path=file_path,
                            line_number=None,
                            column_number=None,
                            severity=IssueSeverity.STYLE,
                            rule_id="format",
                            message="File needs formatting",
                            suggestion="Run 'black' to auto-format this file",
                        )
                    )

        # Parse diff output for specific changes
        current_file = None
        for line in output.splitlines():
            if line.startswith("--- ") and len(line) > 4:
                # Extract just the filename from diff header (before tab or multiple spaces)
                filename_part = line[4:].split()[0] if line[4:].split() else line[4:]
                current_file = filename_part.strip()
            elif line.startswith("@@") and current_file:
                # Extract line numbers from diff header
                match = re.search(r"@@ -(\d+)", line)
                if match:
                    line_num = int(match.group(1))
                    issues.append(
                        Issue(
                            file_path=current_file,
                            line_number=line_num,
                            column_number=None,
                            severity=IssueSeverity.STYLE,
                            rule_id="format",
                            message="Formatting changes needed",
                            code_snippet=None,
                        )
                    )

        summary = (
            f"Found {len(issues)} file(s) that need formatting"
            if issues
            else "All files properly formatted"
        )

        return ParsedOutput(
            tool_name=self.tool_name,
            issues=issues,
            summary=summary,
            fix_command="black ." if issues else None,
            raw_output=output,
        )


class RuffParser(BaseParser):
    """Parser for Ruff linter output."""

    def __init__(self):
        super().__init__("ruff")

    def parse(self, output: str, error: str = "") -> ParsedOutput:
        issues = []
        fixable_issues = []

        # Ruff output format: file.py:line:col: CODE [*] message
        # The [*] indicates the issue is auto-fixable
        pattern = r"^(.+?):(\d+):(\d+): ([A-Z]\d+)(\s+\[\*\])? (.+)$"

        for line in output.splitlines():
            match = re.match(pattern, line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                col_num = int(match.group(3))
                rule_id = match.group(4)
                is_fixable = match.group(5) is not None  # Check if [*] is present
                message = match.group(6)

                # Determine severity based on rule code
                severity = (
                    IssueSeverity.ERROR
                    if rule_id.startswith("E")
                    else IssueSeverity.WARNING
                )

                issue = Issue(
                    file_path=file_path,
                    line_number=line_num,
                    column_number=col_num,
                    severity=severity,
                    rule_id=rule_id,
                    message=message,
                    suggestion=f"See https://docs.astral.sh/ruff/rules/{rule_id.lower()}/",
                )

                issues.append(issue)
                if is_fixable:
                    fixable_issues.append(issue)

        # Count auto-fixable issues
        fixable_count = len(fixable_issues)

        summary = f"Found {len(issues)} issue(s)"
        if fixable_count > 0:
            summary += f" ({fixable_count} auto-fixable)"

        return ParsedOutput(
            tool_name=self.tool_name,
            issues=issues,
            summary=summary,
            fix_command="ruff check --fix ." if fixable_count > 0 else None,
            raw_output=output,
        )


class MyPyParser(BaseParser):
    """Parser for MyPy type checker output."""

    def __init__(self):
        super().__init__("mypy")

    def parse(self, output: str, error: str = "") -> ParsedOutput:
        issues = []

        # MyPy output format: file.py:line: error: message [error-code]
        pattern = r"^(.+?):(\d+):\s*(error|warning|note):\s*(.+?)(?:\s*\[(.+?)\])?$"

        for line in output.splitlines():
            match = re.match(pattern, line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                issue_type = match.group(3)
                message = match.group(4)
                error_code = match.group(5)

                severity = {
                    "error": IssueSeverity.ERROR,
                    "warning": IssueSeverity.WARNING,
                    "note": IssueSeverity.INFO,
                }.get(issue_type, IssueSeverity.ERROR)

                issues.append(
                    Issue(
                        file_path=file_path,
                        line_number=line_num,
                        column_number=None,
                        severity=severity,
                        rule_id=error_code,
                        message=message,
                        suggestion="Add type annotations or fix type errors",
                    )
                )

        # Extract summary from MyPy output
        summary_match = re.search(r"Found (\d+) error[s]? in (\d+) file[s]?", output)
        if summary_match:
            summary = f"Found {summary_match.group(1)} error(s) in {summary_match.group(2)} file(s)"
        else:
            summary = f"Found {len(issues)} type issue(s)"

        return ParsedOutput(
            tool_name=self.tool_name, issues=issues, summary=summary, raw_output=output
        )


class TyParser(BaseParser):
    """Parser for Ty type checker output."""

    def __init__(self):
        super().__init__("ty")

    def parse(self, output: str, error: str = "") -> ParsedOutput:
        issues = []

        # Ty output format is similar to MyPy
        # file.py:line:col: error: message
        pattern = r"^(.+?):(\d+):(\d+):\s*(error|warning|note):\s*(.+)$"

        for line in output.splitlines():
            match = re.match(pattern, line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                col_num = int(match.group(3))
                issue_type = match.group(4)
                message = match.group(5)

                severity = {
                    "error": IssueSeverity.ERROR,
                    "warning": IssueSeverity.WARNING,
                    "note": IssueSeverity.INFO,
                }.get(issue_type, IssueSeverity.ERROR)

                issues.append(
                    Issue(
                        file_path=file_path,
                        line_number=line_num,
                        column_number=col_num,
                        severity=severity,
                        rule_id=None,
                        message=message,
                        suggestion="Fix type annotations",
                    )
                )

        summary = (
            f"Found {len(issues)} type issue(s)" if issues else "No type issues found"
        )

        return ParsedOutput(
            tool_name=self.tool_name, issues=issues, summary=summary, raw_output=output
        )


class BanditParser(BaseParser):
    """Parser for Bandit security scanner output."""

    def __init__(self):
        super().__init__("bandit")

    def parse(self, output: str, error: str = "") -> ParsedOutput:
        issues = []

        # Parse Bandit's formatted output
        lines = output.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for issue headers like ">> Issue: [B201:flask_debug_true]"
            if line.startswith(">> Issue:"):
                # Extract issue details
                match = re.search(r"\[([^:]+):([^\]]+)\]", line)
                if match:
                    rule_id = match.group(1)
                    rule_name = match.group(2)

                    # Get severity and confidence from next lines
                    severity_line = ""
                    location_line = ""
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if lines[j].strip().startswith("Severity:"):
                            severity_line = lines[j]
                        elif lines[j].strip().startswith("Location:"):
                            location_line = lines[j]

                    # Parse severity
                    severity_match = re.search(r"Severity:\s*(\w+)", severity_line)
                    severity_str = (
                        severity_match.group(1).lower() if severity_match else "medium"
                    )

                    severity_map = {
                        "high": IssueSeverity.ERROR,
                        "medium": IssueSeverity.WARNING,
                        "low": IssueSeverity.INFO,
                    }
                    severity = severity_map.get(severity_str, IssueSeverity.WARNING)

                    # Parse location
                    location_match = re.search(
                        r"Location:\s*(.+?):(\d+)", location_line
                    )
                    if location_match:
                        file_path = location_match.group(1)
                        line_num = int(location_match.group(2))

                        # Get the actual issue message
                        message = (
                            line.split("]", 1)[1].strip() if "]" in line else rule_name
                        )

                        issues.append(
                            Issue(
                                file_path=file_path,
                                line_number=line_num,
                                column_number=None,
                                severity=severity,
                                rule_id=rule_id,
                                message=message,
                                suggestion=f"Review security implications of {rule_name}",
                            )
                        )
            i += 1

        # Extract summary
        summary_match = re.search(r"Total issues.*?:\s*(\d+)", output)
        if summary_match:
            total_issues = int(summary_match.group(1))
            summary = f"Found {total_issues} security issue(s)"
        else:
            summary = f"Found {len(issues)} security issue(s)"

        return ParsedOutput(
            tool_name=self.tool_name, issues=issues, summary=summary, raw_output=output
        )


class MarkdownlintParser(BaseParser):
    """Parser for Markdownlint output."""

    def __init__(self):
        super().__init__("markdownlint")

    def parse(self, output: str, error: str = "") -> ParsedOutput:
        issues = []

        # Markdownlint output format: file.md:line:col MD001/heading-increment message
        # or file.md:line MD001/heading-increment message
        pattern = r"^(.+?):(\d+)(?::(\d+))?\s+(MD\d+)/([^\s]+)\s+(.+)$"

        for line in output.splitlines():
            match = re.match(pattern, line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                col_num = int(match.group(3)) if match.group(3) else None
                rule_id = match.group(4)
                rule_name = match.group(5)
                message = match.group(6)

                issues.append(
                    Issue(
                        file_path=file_path,
                        line_number=line_num,
                        column_number=col_num,
                        severity=IssueSeverity.STYLE,
                        rule_id=f"{rule_id}/{rule_name}",
                        message=message,
                        suggestion=f"See https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md#{rule_id.lower()}",
                    )
                )

        summary = (
            f"Found {len(issues)} markdown style issue(s)"
            if issues
            else "All markdown files pass linting"
        )

        return ParsedOutput(
            tool_name=self.tool_name, issues=issues, summary=summary, raw_output=output
        )


class GitleaksParser(BaseParser):
    """Parser for Gitleaks secrets scanner output."""

    def __init__(self):
        super().__init__("gitleaks")

    def parse(self, output: str, error: str = "") -> ParsedOutput:
        issues = []

        # Gitleaks outputs findings to stderr in a specific format
        # Finding: secret in file.py
        # Secret: xxx
        # Line: 42

        lines = (error or output).splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("Finding:"):
                # Extract file path
                file_match = re.search(r"Finding:\s*.+?\s+in\s+(.+)", line)
                if file_match:
                    file_path = file_match.group(1)

                    # Look for line number
                    line_num = None
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if lines[j].startswith("Line:"):
                            line_match = re.search(r"Line:\s*(\d+)", lines[j])
                            if line_match:
                                line_num = int(line_match.group(1))
                            break

                    # Extract description
                    desc_match = re.search(r"Finding:\s*(.+?)\s+in", line)
                    description = (
                        desc_match.group(1) if desc_match else "Potential secret found"
                    )

                    issues.append(
                        Issue(
                            file_path=file_path,
                            line_number=line_num,
                            column_number=None,
                            severity=IssueSeverity.ERROR,
                            rule_id="secret",
                            message=description,
                            suggestion="Remove secrets from code and use environment variables or secret management tools",
                        )
                    )
            i += 1

        summary = (
            f"Found {len(issues)} potential secret(s)"
            if issues
            else "No secrets detected"
        )

        return ParsedOutput(
            tool_name=self.tool_name,
            issues=issues,
            summary=summary,
            raw_output=output or error,
        )


class SemgrepParser(BaseParser):
    """Parser for Semgrep security scanner output."""

    def __init__(self):
        super().__init__("semgrep")

    def parse(self, output: str, error: str = "") -> ParsedOutput:
        issues = []

        # Semgrep output includes findings in a specific format
        # file.py:line:col: rule-id: message
        pattern = r"^(.+?):(\d+):(\d+):\s*([^:]+):\s*(.+)$"

        for line in output.splitlines():
            match = re.match(pattern, line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                col_num = int(match.group(3))
                rule_id = match.group(4).strip()
                message = match.group(5).strip()

                # Determine severity based on rule naming conventions
                severity = IssueSeverity.ERROR
                if "audit" in rule_id.lower():
                    severity = IssueSeverity.INFO
                elif "warning" in rule_id.lower():
                    severity = IssueSeverity.WARNING

                issues.append(
                    Issue(
                        file_path=file_path,
                        line_number=line_num,
                        column_number=col_num,
                        severity=severity,
                        rule_id=rule_id,
                        message=message,
                        suggestion="Review and fix the security vulnerability",
                    )
                )

        # Extract summary from Semgrep output
        summary_match = re.search(
            r"ran (\d+) rules.*?(\d+) findings", output, re.IGNORECASE
        )
        if summary_match:
            summary = f"Ran {summary_match.group(1)} rules, found {summary_match.group(2)} findings"
        else:
            summary = f"Found {len(issues)} security issue(s)"

        return ParsedOutput(
            tool_name=self.tool_name, issues=issues, summary=summary, raw_output=output
        )


class SafetyParser(BaseParser):
    """Parser for Safety vulnerability scanner output."""

    def __init__(self):
        super().__init__("safety")

    def parse(self, output: str, error: str = "") -> ParsedOutput:
        issues = []

        # Safety scan output includes vulnerability details
        # Looking for patterns like:
        # -> Vulnerability found in package_name version X.Y.Z
        # Vulnerability ID: CVE-XXXX-YYYY or GHSA-XXXX

        lines = (output or error).splitlines()
        current_package = None
        current_version = None
        current_vulnerability = None

        for line in lines:
            # Check for package vulnerability
            vuln_match = re.search(
                r"Vulnerability found in (\S+) version ([\d.]+)", line
            )
            if vuln_match:
                current_package = vuln_match.group(1)
                current_version = vuln_match.group(2)

            # Check for vulnerability ID
            id_match = re.search(
                r"Vulnerability ID:\s*(CVE-\d{4}-\d+|GHSA-[\w-]+)", line
            )
            if id_match:
                current_vulnerability = id_match.group(1)

            # Check for severity
            severity_match = re.search(r"Severity:\s*(\w+)", line, re.IGNORECASE)
            if severity_match and current_package:
                severity_str = severity_match.group(1).lower()
                severity_map = {
                    "critical": IssueSeverity.ERROR,
                    "high": IssueSeverity.ERROR,
                    "medium": IssueSeverity.WARNING,
                    "low": IssueSeverity.INFO,
                }
                severity = severity_map.get(severity_str, IssueSeverity.WARNING)

                # Create issue for this vulnerability
                message = f"Vulnerability in {current_package} version {current_version}" if current_version else f"Vulnerability in {current_package}"
                issues.append(
                    Issue(
                        file_path="requirements.txt",  # Safety checks requirements files
                        line_number=None,
                        column_number=None,
                        severity=severity,
                        rule_id=current_vulnerability or "vulnerability",
                        message=message,
                        suggestion=f"Update {current_package} to a secure version",
                    )
                )
                current_package = None
                current_version = None
                current_vulnerability = None

        # Check for summary in output
        if "No vulnerabilities found" in output or "0 vulnerabilities found" in output:
            summary = "No vulnerabilities found in dependencies"
        else:
            summary = f"Found {len(issues)} vulnerability(ies) in dependencies"

        return ParsedOutput(
            tool_name=self.tool_name,
            issues=issues,
            summary=summary,
            raw_output=output or error,
        )


class TFLintParser(BaseParser):
    """Parser for TFLint output."""

    def __init__(self):
        super().__init__("tflint")

    def parse(self, output: str, error: str = "") -> ParsedOutput:
        issues = []

        # TFLint output format: file.tf:line:col: message [rule_name]
        pattern = r"^(.+?):(\d+):(\d+):\s*(.+?)(?:\s*\[(.+?)\])?$"

        for line in output.splitlines():
            match = re.match(pattern, line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                col_num = int(match.group(3))
                message = match.group(4).strip()
                rule_name = match.group(5)

                # Determine severity based on message
                severity = IssueSeverity.WARNING
                if "error" in message.lower():
                    severity = IssueSeverity.ERROR
                elif "notice" in message.lower():
                    severity = IssueSeverity.INFO

                issues.append(
                    Issue(
                        file_path=file_path,
                        line_number=line_num,
                        column_number=col_num,
                        severity=severity,
                        rule_id=rule_name,
                        message=message,
                        suggestion="Review Terraform best practices",
                    )
                )

        summary = f"Found {len(issues)} issue(s)" if issues else "No issues found"

        return ParsedOutput(
            tool_name=self.tool_name, issues=issues, summary=summary, raw_output=output
        )


class TerraformParser(BaseParser):
    """Parser for Terraform fmt output."""

    def __init__(self):
        super().__init__("terraform")

    def parse(self, output: str, error: str = "") -> ParsedOutput:
        issues = []

        # Terraform fmt lists files that need formatting
        for line in output.splitlines():
            if line.strip() and line.endswith(".tf"):
                issues.append(
                    Issue(
                        file_path=line.strip(),
                        line_number=None,
                        column_number=None,
                        severity=IssueSeverity.STYLE,
                        rule_id="format",
                        message="File needs formatting",
                        suggestion="Run 'terraform fmt' to auto-format this file",
                    )
                )

        summary = (
            f"Found {len(issues)} file(s) that need formatting"
            if issues
            else "All Terraform files properly formatted"
        )

        return ParsedOutput(
            tool_name=self.tool_name,
            issues=issues,
            summary=summary,
            fix_command="terraform fmt -recursive" if issues else None,
            raw_output=output,
        )


# Registry of parsers
PARSERS: Dict[str, BaseParser] = {
    "black": BlackParser(),
    "ruff": RuffParser(),
    "mypy": MyPyParser(),
    "ty": TyParser(),
    "bandit": BanditParser(),
    "semgrep": SemgrepParser(),
    "safety": SafetyParser(),
    "markdown": MarkdownlintParser(),
    "gitleaks": GitleaksParser(),
    "terraform": TerraformParser(),
    "tflint": TFLintParser(),
}


def get_parser(tool_name: str) -> Optional[BaseParser]:
    """Get parser for a specific tool."""
    return PARSERS.get(tool_name)


def parse_output(
    tool_name: str, output: str, error: str = ""
) -> Optional[ParsedOutput]:
    """Parse output for a specific tool."""
    parser = get_parser(tool_name)
    if parser:
        return parser.parse(output, error)
    return None
