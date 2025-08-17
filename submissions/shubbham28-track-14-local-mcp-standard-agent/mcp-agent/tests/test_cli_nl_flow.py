import json
from client.cli import _execute_plan
from client.orchestrator import ClientConfig


def test_cli_execute_plan_calls_endpoints(monkeypatch):
    # Arrange a fake cfg and intercept _post_json
    cfg = ClientConfig(openai_api_key=None, endpoints={
        "filesystem": "http://fs.local",
        "system": "http://sys.local",
        "browser": "http://br.local",
    })
    calls = []
    def fake_post(url, payload, timeout=15.0):
        calls.append((url, payload))
        return True, {"ok": True, "result": {"echo": payload}}
    import client.cli as cli
    import client.orchestrator as orch
    orch._post_json = fake_post  # type: ignore

    plan = [
        {"tool": "filesystem", "action": "list", "args": {"path": "."}},
        {"tool": "system", "action": "exec", "args": {"cmd": "echo hi"}},
    ]

    results = _execute_plan(plan, cfg)

    assert len(results) == 2
    assert calls[0][0] == cfg.endpoints["filesystem"]
    assert calls[1][0] == cfg.endpoints["system"]
    assert results[0]["ok"] and results[1]["ok"]
