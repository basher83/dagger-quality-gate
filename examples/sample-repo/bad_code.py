"""Example Python file with various issues."""

import subprocess  # nosec - intentionally unsafe for testing


# Type errors
def add_numbers(a, b):
    return a + b  # No type hints


result = add_numbers("string", 123)  # Type mismatch


# Security issues
def run_command(user_input):
    # Bandit should flag this as dangerous
    subprocess.call(user_input, shell=True)  # nosec


# Unused imports and variables
import sys  # noqa: F401

unused_variable = 42

# Style issues (long line)
really_long_variable_name_that_exceeds_the_typical_line_length_limit_and_should_be_flagged_by_linters = (
    "This line is way too long"
)


# Missing docstrings on class
class BadClass:
    def method_without_docstring(self):
        pass
