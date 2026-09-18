"""Tests for the repository's GitHub Actions workflow."""

from pathlib import Path

import yaml


WORKFLOW_PATH = (
    Path(__file__).parent.parent / ".github" / "workflows" / "python-package.yml"
)


def load_workflow_text() -> str:
    """Return the workflow file as text."""
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def load_workflow() -> dict:
    """Parse and return the workflow configuration."""
    workflow = yaml.safe_load(load_workflow_text())
    assert isinstance(workflow, dict)
    return workflow


def test_workflow_exists_and_is_not_empty() -> None:
    assert WORKFLOW_PATH.is_file()
    assert load_workflow_text().strip()


def test_workflow_is_valid_yaml() -> None:
    assert load_workflow()


def test_expected_jobs_are_present() -> None:
    jobs = load_workflow()["jobs"]
    assert "build_test_lint" in jobs
    assert "publish" in jobs


def test_build_job_runs_lint_and_tests() -> None:
    text = load_workflow_text()
    assert "flake8" in text
    assert "pytest -q" in text


def test_publish_job_uses_pypi_action() -> None:
    text = load_workflow_text()
    assert "pypa/gh-action-pypi-publish" in text
    assert "PYPI_API_TOKEN" in text


def test_workflow_uses_checkout() -> None:
    assert "actions/checkout@v4" in load_workflow_text()


def test_stale_action_configuration_is_present() -> None:
    text = load_workflow_text()
    assert "actions/stale@v9" in text
    assert "repo-token: ${{ secrets.GITHUB_TOKEN }}" in text
    assert "only-issue-types: issues" in text
    assert "labels-to-add-when-unstale:" in text
    assert "labels-to-remove-when-stale:" in text


def test_workflow_triggers_on_main_push_and_pull_request() -> None:
    text = load_workflow_text()
    assert 'branches: [ "main" ]' in text
    assert "pull_request:" in text
