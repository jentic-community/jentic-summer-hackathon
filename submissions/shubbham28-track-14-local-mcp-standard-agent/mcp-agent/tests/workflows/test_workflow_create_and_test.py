import os
import uuid
import pytest  # type: ignore

# Integration test for orchestrated create+fix workflow

from client.orchestrator import load_client_config, run_workflow_create_and_test, system_exec, fs_read


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("SYSTEM_SERVER_ENDPOINT") is None or os.environ.get("FS_SERVER_ENDPOINT") is None,
    reason="Requires filesystem and system servers to be running",
)
def test_workflow_create_and_fix():
    cfg = load_client_config()

    # Ensure pytest is available in the environment (allowed by allowlist)
    prep = system_exec("pytest -q -h", timeout_sec=30, cfg=cfg)
    assert prep.get("ok"), f"pytest not available or blocked: {prep}"

    summary = run_workflow_create_and_test(cfg)

    assert isinstance(summary, dict)
    assert "before_failures" in summary and "after_failures" in summary
    assert summary["before_failures"] > 0
    assert summary["after_failures"] == 0

    # Sanity check edited files exist
    for p in summary.get("edited_files", []):
        got = fs_read(p, cfg)
        assert got.get("ok"), f"File missing: {p}"
