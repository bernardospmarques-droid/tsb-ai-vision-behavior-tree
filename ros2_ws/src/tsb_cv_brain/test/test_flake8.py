"""Run Flake8 while excluding non-functional style preferences."""

import pytest
from ament_flake8.main import main_with_errors

IGNORED_CODES = (
    ': Q000 ',
    ': I100 ',
)


@pytest.mark.flake8
@pytest.mark.linter
def test_flake8():
    """Check Python code for relevant Flake8 problems."""
    _, errors = main_with_errors(argv=[])

    relevant_errors = [
        error
        for error in errors
        if not any(
            code in error
            for code in IGNORED_CODES
        )
    ]

    assert not relevant_errors, (
        'Found %d relevant code style errors or warnings:\n'
        % len(relevant_errors)
        + '\n'.join(relevant_errors)
    )
