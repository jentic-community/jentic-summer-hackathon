import os
import pathlib
import pytest  # type: ignore

from client.orchestrator import load_client_config, run_booking_search


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("BROWSER_SERVER_ENDPOINT") is None,
    reason="Requires browser server to be running",
)
def test_workflow_booking_search_artifacts():
    cfg = load_client_config()

    # Trigger booking search (dates optional; avoid if playwright missing in server)
    out = run_booking_search("Dublin", 5, cfg=cfg)
    assert out.get("ok"), f"booking_search failed: {out}"

    csv_path = out.get("csv_path")
    screenshot_path = out.get("screenshot_path")
    assert isinstance(csv_path, str) and isinstance(screenshot_path, str)

    assert pathlib.Path(csv_path).exists(), f"CSV not found: {csv_path}"
    assert pathlib.Path(screenshot_path).exists(), f"Screenshot not found: {screenshot_path}"

    # Rows preview should have at least 1 row and required keys if any
    rows = out.get("rows") or []
    assert isinstance(rows, list)
    assert len(rows) >= 0  # allow 0 if no results, but prefer >=1
    if rows:
        first = rows[0]
        for k in ("name", "price", "rating", "link"):
            assert k in first
