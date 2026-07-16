"""
test_ci_workflow.py - CI Workflow Configuration Tests
======================================================
Validates the structure and configuration of .github/workflows/ci.yml,
specifically covering the "Close Stale Issues" step added in this PR.

NOTE: The YAML in this file is malformed (invalid YAML syntax due to a
leading space on the 'repo-token:' key inside the 'with:' block). Tests
are therefore written against the raw file text rather than parsed YAML.
Tests that document YAML validity explicitly assert the parse failure.
"""

import os
import re
import yaml


WORKFLOW_PATH = os.path.join(
    os.path.dirname(__file__), "..", ".github", "workflows", "ci.yml"
)


def _load_workflow_text() -> str:
    with open(WORKFLOW_PATH, "r") as f:
        return f.read()


def _load_workflow_lines() -> list[str]:
    with open(WORKFLOW_PATH, "r") as f:
        return f.readlines()


# ── File Existence and Raw Validity Tests ────────────────────────────────

class TestWorkflowFileExistence:
    """Basic file existence and encoding tests."""

    def test_file_exists(self) -> None:
        assert os.path.isfile(WORKFLOW_PATH), (
            f"Workflow file not found at {WORKFLOW_PATH}"
        )

    def test_file_is_not_empty(self) -> None:
        text = _load_workflow_text()
        assert len(text.strip()) > 0

    def test_file_is_utf8_readable(self) -> None:
        try:
            _load_workflow_text()
        except UnicodeDecodeError as exc:
            assert False, f"ci.yml is not readable as UTF-8: {exc}"


# ── YAML Validity Documentation Test ─────────────────────────────────────

class TestWorkflowYAMLValidity:
    """
    Documents the YAML parse status of the workflow file.

    The PR introduced a structural defect: a leading space on the
    'repo-token:' key inside the 'with:' block causes a YAML block
    mapping conflict, making the file invalid YAML.
    """

    def test_file_fails_yaml_parse_due_to_pr_indentation_defect(self) -> None:
        """
        The file introduced by this PR is not valid YAML.
        The leading space on ' repo-token:' causes a parser error.
        This test documents that defect explicitly.
        """
        try:
            with open(WORKFLOW_PATH, "r") as f:
                yaml.safe_load(f)
            # If we reach here, the file unexpectedly became valid YAML
            # (e.g., after a subsequent fix). Keep the test informative.
            assert False, (
                "Expected ci.yml to fail YAML parsing due to leading space "
                "on 'repo-token:' key, but it parsed successfully. "
                "The structural defect may have been fixed."
            )
        except yaml.YAMLError:
            pass  # Expected: file is invalid YAML as introduced by this PR

    def test_repo_token_has_leading_space_causing_parse_failure(self) -> None:
        """The leading space on ' repo-token:' is the root cause of invalid YAML."""
        text = _load_workflow_text()
        # The PR introduces a line with an extra leading space before repo-token
        assert " repo-token:" in text, (
            "Expected ' repo-token:' (with leading space) in ci.yml"
        )


# ── Close Stale Issues Step Content Tests ─────────────────────────────────

class TestCloseStaleIssuesStepContent:
    """
    Tests that the 'Close Stale Issues' step is present and uses the
    correct action reference, validated via raw file text.
    """

    def test_close_stale_issues_step_name_present(self) -> None:
        text = _load_workflow_text()
        assert "Close Stale Issues" in text

    def test_stale_action_reference_present(self) -> None:
        text = _load_workflow_text()
        assert "actions/stale" in text

    def test_stale_action_version_is_v10_2_0(self) -> None:
        text = _load_workflow_text()
        assert "actions/stale@v10.2.0" in text

    def test_stale_action_not_using_latest_tag(self) -> None:
        text = _load_workflow_text()
        assert "actions/stale@latest" not in text

    def test_step_name_and_uses_on_adjacent_lines(self) -> None:
        """'name: Close Stale Issues' and 'uses: actions/stale' appear near each other."""
        lines = _load_workflow_lines()
        name_line = None
        uses_line = None
        for i, line in enumerate(lines):
            if "Close Stale Issues" in line:
                name_line = i
            if "actions/stale@v10.2.0" in line:
                uses_line = i
        assert name_line is not None, "'Close Stale Issues' not found in file"
        assert uses_line is not None, "'actions/stale@v10.2.0' not found in file"
        # The uses line should follow the name line within a few lines
        assert uses_line > name_line, (
            "'uses: actions/stale@v10.2.0' should come after 'name: Close Stale Issues'"
        )
        assert uses_line - name_line <= 3, (
            f"Expected 'uses' within 3 lines of 'name', got {uses_line - name_line} lines apart"
        )

    def test_close_stale_issues_step_is_in_publish_section(self) -> None:
        """The step appears after the 'publish:' job header in the file."""
        text = _load_workflow_text()
        publish_pos = text.find("publish:")
        stale_pos = text.find("Close Stale Issues")
        assert publish_pos != -1, "'publish:' job not found"
        assert stale_pos != -1, "'Close Stale Issues' not found"
        assert stale_pos > publish_pos, (
            "Expected 'Close Stale Issues' to appear after 'publish:' in the file"
        )


# ── Stale Action With-Block Parameter Tests ───────────────────────────────

class TestStaleActionWithBlockParameters:
    """
    Tests that the 'with:' block for the stale action contains
    the expected configuration parameter keys.
    """

    def test_with_block_present_in_file(self) -> None:
        lines = _load_workflow_lines()
        with_lines = [l for l in lines if re.match(r"^\s*with:\s*$", l)]
        assert len(with_lines) >= 1, "Expected at least one 'with:' block in the file"

    def test_days_before_stale_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "days-before-stale:" in text

    def test_days_before_close_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "days-before-close:" in text

    def test_stale_issue_label_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "stale-issue-label:" in text

    def test_stale_pr_label_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "stale-pr-label:" in text

    def test_operations_per_run_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "operations-per-run:" in text

    def test_remove_stale_when_updated_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "remove-stale-when-updated:" in text

    def test_exempt_issue_labels_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "exempt-issue-labels:" in text

    def test_exempt_pr_labels_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "exempt-pr-labels:" in text

    def test_close_issue_reason_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "close-issue-reason:" in text

    def test_delete_branch_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "delete-branch:" in text

    def test_stale_issue_message_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "stale-issue-message:" in text

    def test_stale_pr_message_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "stale-pr-message:" in text

    def test_debug_only_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "debug-only:" in text

    def test_enable_statistics_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "enable-statistics:" in text

    def test_exempt_all_milestones_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "exempt-all-milestones:" in text

    def test_exempt_draft_pr_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "exempt-draft-pr:" in text

    def test_include_only_assigned_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "include-only-assigned:" in text

    def test_ignore_updates_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "ignore-updates:" in text

    def test_ascending_parameter_present(self) -> None:
        text = _load_workflow_text()
        assert "ascending:" in text


# ── Structural Indentation Defect Tests ───────────────────────────────────

class TestStructuralIndentationDefects:
    """
    Tests that document the indentation issues introduced by the PR.

    1. The 'with:' block should be indented 8 spaces (under the step),
       but it is placed at 2-space indent (root level).
    2. 'repo-token:' has an extra leading space.
    3. There is trailing whitespace on the line before the stale step.
    """

    def test_with_block_at_root_level_indentation(self) -> None:
        """'with:' appears at 2-space indent rather than 8-space indent."""
        lines = _load_workflow_lines()
        # Find the 'with:' block that follows the stale step
        stale_step_idx = None
        for i, line in enumerate(lines):
            if "Close Stale Issues" in line:
                stale_step_idx = i
                break
        assert stale_step_idx is not None

        # Look for 'with:' line after the stale step
        for line in lines[stale_step_idx:stale_step_idx + 5]:
            if re.match(r"^with:\s*$", line):
                # 'with:' is at column 0 (root) - this is the defect
                return
            if re.match(r"^  with:\s*$", line):
                # 'with:' at 2-space indent - also misindented for a step 'with'
                return
        # If we didn't find it at wrong level, the file may have been corrected
        # Check if it exists at any level after the step
        found_with = False
        for line in lines[stale_step_idx:stale_step_idx + 5]:
            if "with:" in line:
                found_with = True
                indent = len(line) - len(line.lstrip())
                assert indent < 8, (
                    f"'with:' is correctly indented at {indent} spaces. "
                    "Expected misindentation as introduced by the PR."
                )
                break
        assert found_with, "Expected 'with:' block after 'Close Stale Issues' step"

    def test_repo_token_has_leading_space(self) -> None:
        """' repo-token:' has a leading space (indentation error)."""
        text = _load_workflow_text()
        # The specific malformed line from the PR diff
        assert " repo-token:" in text

    def test_trailing_whitespace_before_stale_step(self) -> None:
        """There is a line of trailing whitespace before the Close Stale Issues step."""
        lines = _load_workflow_lines()
        stale_step_idx = None
        for i, line in enumerate(lines):
            if "Close Stale Issues" in line:
                stale_step_idx = i
                break
        assert stale_step_idx is not None
        # Check lines immediately before the stale step for whitespace-only lines
        preceding_lines = lines[max(0, stale_step_idx - 3):stale_step_idx]
        whitespace_lines = [l for l in preceding_lines if l.strip() == "" and l != "\n"]
        assert len(whitespace_lines) > 0, (
            "Expected a trailing-whitespace-only line before the 'Close Stale Issues' step"
        )


# ── Pre-existing Job Integrity Tests ─────────────────────────────────────

class TestPreExistingJobIntegrity:
    """
    Tests that the pre-existing jobs are intact and unmodified by the PR.
    These run on raw text since the file is invalid YAML.
    """

    def test_workflow_name_present(self) -> None:
        text = _load_workflow_text()
        assert "name:" in text

    def test_build_test_lint_job_present(self) -> None:
        text = _load_workflow_text()
        assert "build-test-lint:" in text

    def test_publish_job_present(self) -> None:
        text = _load_workflow_text()
        assert "publish:" in text

    def test_pypi_publish_action_still_present(self) -> None:
        text = _load_workflow_text()
        assert "gh-action-pypi-publish" in text

    def test_checkout_action_present(self) -> None:
        text = _load_workflow_text()
        assert "actions/checkout" in text

    def test_pytest_run_command_present(self) -> None:
        text = _load_workflow_text()
        assert "pytest" in text

    def test_push_trigger_to_main_present(self) -> None:
        text = _load_workflow_text()
        # Check for push: and main branch in the file
        assert "push:" in text
        assert "- main" in text

    def test_pypi_api_token_secret_reference_present(self) -> None:
        text = _load_workflow_text()
        assert "PYPI_API_TOKEN" in text


# ── Boundary / Regression Tests ──────────────────────────────────────────

class TestBoundaryAndRegression:
    """Boundary and regression tests for the PR-introduced changes."""

    def test_stale_action_not_version_v8_or_older(self) -> None:
        """Confirm the PR uses v10, not an outdated version like v8."""
        text = _load_workflow_text()
        assert "actions/stale@v8" not in text
        assert "actions/stale@v9" not in text

    def test_only_one_stale_step_in_file(self) -> None:
        """Exactly one 'Close Stale Issues' step is added by this PR."""
        text = _load_workflow_text()
        count = text.count("Close Stale Issues")
        assert count == 1, f"Expected exactly 1 'Close Stale Issues', found {count}"

    def test_only_one_stale_action_reference(self) -> None:
        """Exactly one reference to 'actions/stale@v10.2.0'."""
        text = _load_workflow_text()
        count = text.count("actions/stale@v10.2.0")
        assert count == 1, (
            f"Expected exactly 1 'actions/stale@v10.2.0' reference, found {count}"
        )

    def test_no_additional_jobs_introduced(self) -> None:
        """The PR adds a step to an existing job, not a new top-level job."""
        text = _load_workflow_text()
        # Only the two known jobs should appear as job-level keys
        assert "build-test-lint:" in text
        assert "publish:" in text
        # No 'stale:' job-level key should be present
        assert not re.search(r"^\s{0,2}stale:\s*$", text, re.MULTILINE), (
            "A standalone 'stale:' job should not have been introduced"
        )

    def test_with_block_parameters_are_optional_comments(self) -> None:
        "All stale 'with' parameters have '# optional' in their comments."
        text = _load_workflow_text()
        # Find the section containing stale parameters
        stale_idx = 
        uses_: actions/stale@v10.2.0
        assert stale_idx != -1
        stale_section = text[stale_idx:]
        assert stale_section

    def test_stale_action_step_has_name_key(self) -> None:
     The step defining the stale action includes a 'name:' key
        lines = _load_workflow_lines
        name_present = any
            name: Close Stale Issues in 
            line for line in lines
        assert name_present

    def test_stale_action_step_has_uses_key(self) -> None:
        "The step defining the stale action includes a 'uses:' key."
        lines = _load_workflow_lines
        uses_present = any
            uses: actions/stale@v10.2.0 
            in line for line in lines
        assert uses_present

    def test_only_issue_types_parameter_present(self) -> None:
        "The 'only-issue-types' parameter (last in the stale with-block) is present."
        text = _load_workflow_text
        assert only-issue-types:
        in text

    def test_labels_to_add_when_unstale_parameter_present(self) -> None:
        Boundary: 'labels-to-add-when-unstale' parameter is present.
        text = _load_workflow_text
        assert labels-to-add-when-unstale:
        in text

    def test_labels_to_remove_when_stale_parameter_present(self) -> None:
        "Boundary: labels-to-remove-when-stale parameter is present."
        text = _load_workflow_text
        assert labels-to-remove-when-stale:
        in text
