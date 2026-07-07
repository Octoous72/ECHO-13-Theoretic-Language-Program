 coderabbitai/autofix/ade27d8
"""
test_azure_functions_workflow.py - Azure Functions Workflow Tests
==================================================================
Validates the structure and configuration of
.github/workflows/azure-functions-app-python.yml,
specifically covering the "Run Azure Functions Action" step and the
surrounding build step that was modified in the PR.

The PR introduced structural defects:
  - `client-id` inserted as bare text inside the pip-install run: block
  - The `Run Azure Functions Action` step was embedded inside the run:
    shell script instead of being a top-level step
  - `-with:` appeared as an invalid YAML mapping key
  - The `id: fa` field on the step was removed
These tests document and verify the corrected (expected) structure.
"""

import os

import yaml

WORKFLOW_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".github",
    "workflows",
    "azure-functions-app-python.yml",
)


def _load_workflow_text() -> str:
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _load_workflow_lines() -> list[str]:
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return f.readlines()


def _load_workflow_yaml() -> dict:
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── File Existence and Raw Validity Tests ─────────────────────────────────────


class TestAzureWorkflowFileExistence:
    """Basic file existence and encoding tests."""

    def test_file_exists(self) -> None:
        assert os.path.isfile(
            WORKFLOW_PATH
        ), f"Workflow file not found at {WORKFLOW_PATH}"

    def test_file_is_not_empty(self) -> None:
        text = _load_workflow_text()
        assert len(text.strip()) > 0

    def test_file_is_utf8_readable(self) -> None:
        try:
            _load_workflow_text()
        except UnicodeDecodeError as exc:
            raise AssertionError(
                f"azure-functions-app-python.yml is not readable as " f"UTF-8: {exc}"
            )


# ── YAML Validity and Top-Level Structure Tests ───────────────────────────────


class TestAzureWorkflowYAMLValidity:
    """Tests that the workflow file is valid YAML with the expected top-level keys."""

    def test_file_is_valid_yaml(self) -> None:
        """The file must be parseable as valid YAML."""
        try:
            _load_workflow_yaml()
        except yaml.YAMLError as exc:
            raise AssertionError(
                f"azure-functions-app-python.yml failed YAML parse: {exc}"
            )

    def test_top_level_name_key_present(self) -> None:
        data = _load_workflow_yaml()
        assert "name" in data, "Top-level 'name' key missing from workflow"

    def test_top_level_on_key_present(self) -> None:
        data = _load_workflow_yaml()
        assert "on" in data, "Top-level 'on' (trigger) key missing from workflow"

    def test_top_level_env_key_present(self) -> None:
        data = _load_workflow_yaml()
        assert "env" in data, "Top-level 'env' key missing from workflow"

    def test_top_level_jobs_key_present(self) -> None:
        data = _load_workflow_yaml()
        assert "jobs" in data, "Top-level 'jobs' key missing from workflow"

    def test_workflow_name_is_correct(self) -> None:
        data = _load_workflow_yaml()
        assert "Deploy Python project to Azure Function App" in data.get(
            "name", ""
        ), "Workflow name does not match expected value"

    def test_push_trigger_targets_main_branch(self) -> None:
        data = _load_workflow_yaml()
        # PyYAML may parse "on" as boolean True
        on_config = data.get("on") or data.get(True) or {}
        if on_config is True:
            on_config = {}
        branches = on_config.get("push", {}).get("branches", [])
        assert "main" in branches, "Workflow should trigger on push to 'main' branch"


# ── Environment Variables Tests ───────────────────────────────────────────────


class TestAzureWorkflowEnvVariables:
    """Tests that required environment variables are defined."""

    def test_azure_functionapp_name_env_defined(self) -> None:
        data = _load_workflow_yaml()
        env = data.get("env", {})
        assert (
            "AZURE_FUNCTIONAPP_NAME" in env
        ), "AZURE_FUNCTIONAPP_NAME must be defined in env"

    def test_azure_functionapp_package_path_env_defined(self) -> None:
        data = _load_workflow_yaml()
        env = data.get("env", {})
        assert (
            "AZURE_FUNCTIONAPP_PACKAGE_PATH" in env
        ), "AZURE_FUNCTIONAPP_PACKAGE_PATH must be defined in env"

    def test_python_version_env_defined(self) -> None:
        data = _load_workflow_yaml()
        env = data.get("env", {})
        assert "PYTHON_VERSION" in env, "PYTHON_VERSION must be defined in env"


# ── Job Structure Tests ───────────────────────────────────────────────────────


class TestAzureWorkflowJobStructure:
    """Tests that the build-and-deploy job has the correct structure."""

    def test_build_and_deploy_job_exists(self) -> None:
        data = _load_workflow_yaml()
        jobs = data.get("jobs", {})
        assert "build-and-deploy" in jobs, "Expected 'build-and-deploy' job in workflow"

    def test_build_and_deploy_runs_on_ubuntu(self) -> None:
        data = _load_workflow_yaml()
        job = data["jobs"]["build-and-deploy"]
        assert (
            job.get("runs-on") == "ubuntu-latest"
        ), "build-and-deploy job should run on ubuntu-latest"

    def test_build_and_deploy_has_steps(self) -> None:
        data = _load_workflow_yaml()
        job = data["jobs"]["build-and-deploy"]
        steps = job.get("steps", [])
        assert len(steps) > 0, "build-and-deploy job must have at least one step"

    def test_build_and_deploy_has_expected_number_of_steps(self) -> None:
        """The job should have 4 distinct steps, not fewer (which would
        indicate the Azure Functions step got absorbed into the pip-install
        run block).
        """
        data = _load_workflow_yaml()
        job = data["jobs"]["build-and-deploy"]
        steps = job.get("steps", [])
        assert len(steps) >= 4, (
            f"Expected at least 4 steps in build-and-deploy, found "
            f"{len(steps)}. The 'Run Azure Functions Action' step may have "
            f"been embedded inside the pip-install run: block."
        )


# ── Run Azure Functions Action Step Tests ─────────────────────────────────────


class TestAzureFunctionsActionStep:
    """
    Tests that the 'Run Azure Functions Action' step is a proper top-level
    step, not embedded inside the pip-install run: shell script block.

    The PR introduced a defect where this step's YAML was indented into the
    run: multiline block, making it invisible to GitHub Actions as a step.
    """

    def _get_steps(self) -> list[dict]:
        data = _load_workflow_yaml()
        return data["jobs"]["build-and-deploy"].get("steps", [])

    def _get_azure_functions_step(self) -> dict | None:
        for step in self._get_steps():
            if isinstance(step, dict):
                uses = step.get("uses", "")
                name = step.get("name", "")
                if "functions-action" in str(
                    uses
                ) or "Run Azure Functions Action" in str(name):
                    return step
        return None

    def test_run_azure_functions_action_step_name_present_in_file(self) -> None:
        text = _load_workflow_text()
        assert (
            "Run Azure Functions Action" in text
        ), "'Run Azure Functions Action' step name not found in workflow file"

    def test_azure_functions_action_is_proper_step_not_shell_text(self) -> None:
        """The Azure Functions Action must appear as a parsed step dict,
        not as shell script text embedded inside the pip-install run: block.
        """
        step = self._get_azure_functions_step()
        assert step is not None, (
            "No step with 'uses: Azure/functions-action' found in the "
            "parsed YAML steps. The step may have been embedded inside the "
            "pip-install run: shell block rather than being a top-level "
            "workflow step."
        )

    def test_azure_functions_step_uses_correct_action(self) -> None:
        step = self._get_azure_functions_step()
        assert step is not None, "Azure Functions Action step not found"
        assert "Azure/functions-action" in step.get(
            "uses", ""
        ), "Step should use 'Azure/functions-action'"

    def test_azure_functions_step_uses_v1(self) -> None:
        step = self._get_azure_functions_step()
        assert step is not None, "Azure Functions Action step not found"
        assert step.get("uses", "").endswith(
            "@v1"
        ), "Step should use Azure/functions-action@v1"

    def test_azure_functions_step_has_id(self) -> None:
        """The step must have 'id: fa' — this was removed in the PR defect."""
        step = self._get_azure_functions_step()
        assert step is not None, "Azure Functions Action step not found"
        assert "id" in step, (
            "The 'Run Azure Functions Action' step is missing its 'id' field. "
            "Expected 'id: fa'."
        )

    def test_azure_functions_step_id_is_fa(self) -> None:
        step = self._get_azure_functions_step()
        assert step is not None, "Azure Functions Action step not found"
        assert step.get("id") == "fa", f"Expected step id 'fa', got '{step.get('id')}'"

    def test_azure_functions_step_has_with_block(self) -> None:
        """The step must have a 'with:' block containing action inputs."""
        step = self._get_azure_functions_step()
        assert step is not None, "Azure Functions Action step not found"
        assert "with" in step, (
            "The 'Run Azure Functions Action' step is missing its 'with:' block. "
            "The PR introduced '-with:' as an invalid key."
        )

    def test_azure_functions_step_with_block_is_a_mapping(self) -> None:
        step = self._get_azure_functions_step()
        assert step is not None, "Azure Functions Action step not found"
        with_block = step.get("with")
        assert isinstance(
            with_block, dict
        ), f"Expected 'with:' block to be a dict, got {type(with_block)}"


# ── Azure Functions Action With-Block Parameter Tests ─────────────────────────


class TestAzureFunctionsActionWithBlock:
    """Tests that the 'with:' block for the Azure Functions step contains the
    expected configuration parameters.
    """

    def _get_azure_functions_step(self) -> dict | None:
        data = _load_workflow_yaml()
        steps = data["jobs"]["build-and-deploy"].get("steps", [])
        for step in steps:
            if isinstance(step, dict):
                if "functions-action" in str(step.get("uses", "")):
                    return step
        return None

    def _get_with_block(self) -> dict:
        step = self._get_azure_functions_step()
        assert step is not None, "Azure Functions Action step not found"
        with_block = step.get("with", {})
        assert isinstance(with_block, dict), "with: block must be a dict"
        return with_block

    def test_app_name_parameter_present(self) -> None:
        with_block = self._get_with_block()
        assert (
            "app-name" in with_block
        ), "'app-name' parameter missing from Azure Functions step with: block"

    def test_app_name_references_env_variable(self) -> None:
        text = _load_workflow_text()
        assert (
            "AZURE_FUNCTIONAPP_NAME" in text
        ), "app-name should reference the AZURE_FUNCTIONAPP_NAME env variable"

    def test_package_parameter_present(self) -> None:
        with_block = self._get_with_block()
        assert (
            "package" in with_block
        ), "'package' parameter missing from Azure Functions step with: block"

    def test_package_references_env_variable(self) -> None:
        text = _load_workflow_text()
        assert (
            "AZURE_FUNCTIONAPP_PACKAGE_PATH" in text
        ), "package should reference the AZURE_FUNCTIONAPP_PACKAGE_PATH env variable"

    def test_publish_profile_parameter_present(self) -> None:
        with_block = self._get_with_block()
        assert (
            "publish-profile" in with_block
        ), "'publish-profile' parameter missing from Azure Functions step with: block"

    def test_publish_profile_references_secret(self) -> None:
        text = _load_workflow_text()
        assert (
            "AZURE_FUNCTIONAPP_PUBLISH_PROFILE" in text
        ), "publish-profile should reference the AZURE_FUNCTIONAPP_PUBLISH_PROFILE secret"

    def test_scm_do_build_during_deployment_parameter_present(self) -> None:
        with_block = self._get_with_block()
        assert (
            "scm-do-build-during-deployment" in with_block
        ), "'scm-do-build-during-deployment' parameter missing from with: block"

    def test_scm_do_build_during_deployment_is_true(self) -> None:
        with_block = self._get_with_block()
        val = with_block.get("scm-do-build-during-deployment")
        assert (
            val is True
        ), f"Expected scm-do-build-during-deployment to be true, got {val!r}"

    def test_enable_oryx_build_parameter_present(self) -> None:
        with_block = self._get_with_block()
        assert (
            "enable-oryx-build" in with_block
        ), "'enable-oryx-build' parameter missing from with: block"

    def test_enable_oryx_build_is_true(self) -> None:
        with_block = self._get_with_block()
        val = with_block.get("enable-oryx-build")
        assert val is True, f"Expected enable-oryx-build to be true, got {val!r}"


# ── Structural Defect Regression Tests ───────────────────────────────────────


class TestAzureWorkflowStructuralDefects:
    """
    Regression tests for the specific structural defects introduced by the PR:
    1. 'client-id' bare text inserted inside the pip-install run: block
    2. The Azure Functions step embedded inside the run: shell script
    3. '-with:' appearing as a malformed YAML key
    4. The 'id: fa' field removed from the step
    """

    def test_client_id_not_in_pip_install_run_block(self) -> None:
        """'client-id' must NOT appear as bare text inside the pip-install
        shell script. The PR incorrectly inserted it after 'popd' in the
        run: block.
        """
        data = _load_workflow_yaml()
        steps = data["jobs"]["build-and-deploy"].get("steps", [])
        for step in steps:
            if not isinstance(step, dict):
                continue
            run_script = step.get("run", "")
            if "pip install" in str(run_script) or "popd" in str(run_script):
                assert "client-id" not in str(run_script), (
                    "Found 'client-id' as bare text inside the pip-install "
                    "run: shell block. This is a structural defect from the "
                    "PR."
                )

    def test_no_invalid_dash_with_key_in_file(self) -> None:
        """'-with:' is not valid YAML for a step parameter; the correct key
        is 'with:'.
        """
        text = _load_workflow_text()
        assert "-with:" not in text, (
            "Found '-with:' in workflow file. This is invalid YAML syntax "
            "introduced by the PR (should be 'with:')."
        )

    def test_azure_functions_action_not_embedded_in_shell_run_block(self) -> None:
        """The 'Azure/functions-action' reference must not appear inside any
        run: shell block.
        """
        data = _load_workflow_yaml()
        steps = data["jobs"]["build-and-deploy"].get("steps", [])
        for step in steps:
            if not isinstance(step, dict):
                continue
            run_script = step.get("run", "")
            assert "functions-action" not in str(run_script), (
                "Found 'Azure/functions-action' embedded inside a run: shell "
                "script block. The step definition was incorrectly placed "
                "inside the pip-install run block."
            )

    def test_run_azure_functions_action_name_not_inside_shell_script(self) -> None:
        """'Run Azure Functions Action' step name must not appear as shell
        script text.
        """
        data = _load_workflow_yaml()
        steps = data["jobs"]["build-and-deploy"].get("steps", [])
        for step in steps:
            if not isinstance(step, dict):
                continue
            run_script = step.get("run", "")
            assert "Run Azure Functions Action" not in str(run_script), (
                "Found 'Run Azure Functions Action' inside a run: shell "
                "script. The step was incorrectly embedded inside the "
                "pip-install run: block."
            )

    def test_pip_install_step_ends_at_popd(self) -> None:
        """The pip-install step's run: script should end after 'popd',
        not continue with step definitions.
        """
        data = _load_workflow_yaml()
        steps = data["jobs"]["build-and-deploy"].get("steps", [])
        pip_step_run = None
        for step in steps:
            if not isinstance(step, dict):
                continue
            run_script = step.get("run", "")
            if "pip install -r requirements.txt" in str(run_script):
                pip_step_run = str(run_script)
                break
        assert pip_step_run is not None, "Pip install step not found"
        # The run script should not contain step-definition-like patterns
        assert "uses:" not in pip_step_run, (
            "Found 'uses:' inside the pip-install run: block - step "
            "definition leaked into shell script"
        )
        assert "- name:" not in pip_step_run, (
            "Found '- name:' inside the pip-install run: block - step "
            "definition leaked into shell script"
        )

    def test_step_id_fa_present_on_azure_functions_step(self) -> None:
        """Regression: the 'id: fa' field was removed by the PR defect and
        must be restored.
        """
        data = _load_workflow_yaml()
        steps = data["jobs"]["build-and-deploy"].get("steps", [])
        fa_step = None
        for step in steps:
            if isinstance(step, dict) and step.get("id") == "fa":
                fa_step = step
                break
        assert fa_step is not None, (
            "No step with 'id: fa' found. The PR removed 'id: fa' from the "
            "'Run Azure Functions Action' step."
        )


# ── Pre-existing Workflow Integrity Tests ─────────────────────────────────────


class TestAzureWorkflowPreExistingJobIntegrity:
    """Tests that pre-existing workflow structure is intact and unmodified."""

    def test_checkout_action_step_present(self) -> None:
        data = _load_workflow_yaml()
        steps = data["jobs"]["build-and-deploy"].get("steps", [])
        checkout_steps = [
            s
            for s in steps
            if isinstance(s, dict) and "actions/checkout" in str(s.get("uses", ""))
        ]
        assert (
            len(checkout_steps) >= 1
        ), "Expected at least one 'actions/checkout' step in build-and-deploy"

    def test_setup_python_action_step_present(self) -> None:
        data = _load_workflow_yaml()
        steps = data["jobs"]["build-and-deploy"].get("steps", [])
        setup_steps = [
            s
            for s in steps
            if isinstance(s, dict) and "setup-python" in str(s.get("uses", ""))
        ]
        assert (
            len(setup_steps) >= 1
        ), "Expected at least one 'actions/setup-python' step in build-and-deploy"

    def test_resolve_dependencies_step_present(self) -> None:
        text = _load_workflow_text()
        assert (
            "Resolve Project Dependencies Using Pip" in text
        ), "Pre-existing 'Resolve Project Dependencies Using Pip' step not found"

    def test_pip_install_requirements_command_present(self) -> None:
        text = _load_workflow_text()
        assert (
            "pip install -r requirements.txt" in text
        ), "pip install command missing from workflow"

    def test_python_packages_target_path_in_pip_install(self) -> None:
        text = _load_workflow_text()
        assert (
            ".python_packages/lib/site-packages" in text
        ), "Python packages target path missing from pip install command"

    def test_workflow_environment_is_dev(self) -> None:
        data = _load_workflow_yaml()
        job = data["jobs"]["build-and-deploy"]
        assert (
            job.get("environment") == "dev"
        ), "build-and-deploy job should target the 'dev' environment"


# ── Boundary and Regression Tests ─────────────────────────────────────────────


class TestAzureWorkflowBoundaryAndRegression:
    """Boundary and regression tests for the azure-functions workflow."""

    def test_only_one_azure_functions_action_step(self) -> None:
        """Exactly one step should use Azure/functions-action."""
        data = _load_workflow_yaml()
        steps = data["jobs"]["build-and-deploy"].get("steps", [])
        fa_steps = [
            s
            for s in steps
            if isinstance(s, dict) and "functions-action" in str(s.get("uses", ""))
        ]
        assert (
            len(fa_steps) == 1
        ), f"Expected exactly 1 Azure Functions Action step, found {len(fa_steps)}"

    def test_only_one_build_and_deploy_job(self) -> None:
        data = _load_workflow_yaml()
        jobs = data.get("jobs", {})
        assert (
            len(jobs) == 1
        ), f"Expected exactly 1 job ('build-and-deploy'), found {len(jobs)}: {list(jobs.keys())}"

    def test_azure_functions_action_not_pinned_to_sha(self) -> None:
        """The action uses a version tag, not a SHA pin."""
        text = _load_workflow_text()
        assert (
            "Azure/functions-action@v1" in text
        ), "Azure/functions-action should be pinned to @v1"

    def test_no_duplicate_client_id_key_outside_run_block(self) -> None:
        """'client-id' should not appear as a bare YAML key in the workflow
        steps. The PR introduced it as stray text after 'popd'.
        """
        lines = _load_workflow_lines()
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # A bare 'client-id' line (not a YAML key like 'client-id:'
            # with a value, and not inside a comment) is invalid in a step
            # context
            if stripped == "client-id":
                raise AssertionError(
                    f"Line {i}: Found bare 'client-id' text in workflow "
                    f"file. This was incorrectly inserted after 'popd' in "
                    f"the pip-install run: block."
                )

    def test_publish_profile_secret_name_correct(self) -> None:
        text = _load_workflow_text()
        assert "AZURE_FUNCTIONAPP_PUBLISH_PROFILE" in text

    def test_scm_build_and_oryx_build_flags_in_file(self) -> None:
        text = _load_workflow_text()
        assert "scm-do-build-during-deployment" in text
        assert "enable-oryx-build" in text

    def test_workflow_has_no_tab_characters(self) -> None:
        """YAML must not contain tab characters for indentation."""
        lines = _load_workflow_lines()
        for i, line in enumerate(lines, 1):
            if line.startswith("\t"):
                raise AssertionError(
                    f"Line {i} starts with a tab character, which is "
                    f"invalid in YAML"
                )

    def test_azure_functions_step_uses_key_appears_after_name_key(self) -> None:
        """In the file, 'uses: Azure/functions-action@v1' should appear after
        the step's 'name:' declaration, not before it.
        """
        lines = _load_workflow_lines()
        name_line_idx = None
        uses_line_idx = None
        for i, line in enumerate(lines):
            if "Run Azure Functions Action" in line and name_line_idx is None:
                name_line_idx = i
            if "Azure/functions-action@v1" in line and uses_line_idx is None:
                uses_line_idx = i
        assert (
            name_line_idx is not None
        ), "'Run Azure Functions Action' not found in file"
        assert (
            uses_line_idx is not None
        ), "'Azure/functions-action@v1' not found in file"
        assert uses_line_idx > name_line_idx, (
            "'uses: Azure/functions-action@v1' should appear after the step "
            "name declaration"
        )
        assert uses_line_idx - name_line_idx <= 5, (
    -m py_compile        f"'uses:' appeared {uses_line_idx - name_line_idx} lines after "
            f"'name:', expected <= 5"
name: Deploy Python project to Azure Function App

on:
  push:
    branches: [ "main" ]

env:
  AZURE_FUNCTIONAPP_NAME: ${{ secrets.AZURE_FUNCTIONAPP_NAME }}
  AZURE_FUNCTIONAPP_PACKAGE_PATH: "."
  PYTHON_VERSION: "3.10"

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment: dev

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Resolve Project Dependencies Using Pip
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt --target=".python_packages/lib/site-packages"
          pushd .
          popd

      - name: 'Run Azure Functions Action'
        uses: Azure/functions-action@v1
        with:
        app-name: ${{ env.AZURE_FUNCTIONAPP_NAME }}
        package: $.       {{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
    publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
    scm-do-build-during-deployment: true
    enable-oryx-build: true
 main
