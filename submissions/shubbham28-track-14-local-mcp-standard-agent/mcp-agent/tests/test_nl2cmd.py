import json
from client.nl2cmd import NaturalLanguagePlanner


class DummyClient:
    class chat:
        class completions:
            @staticmethod
            def create(model=None, temperature=None, messages=None, response_format=None):
                class R:
                    class Choice:
                        class Message:
                            content = json.dumps([
                                {"tool": "filesystem", "action": "list", "args": {"path": "."}},
                                {"tool": "system", "action": "exec", "args": {"cmd": "echo hello"}},
                            ])
                        message = Message()
                    choices = [Choice()]
                return R()


def test_planner_parses_valid_json(monkeypatch):
    # Patch OpenAI client inside planner
    import client.nl2cmd as nl

    nl.OpenAI = lambda api_key=None: DummyClient()  # type: ignore

    planner = NaturalLanguagePlanner(api_key="test-key", model="gpt-3.5-turbo")
    plan = planner.plan("List files and say hello")
    assert isinstance(plan, list)
    assert plan and plan[0]["tool"] == "filesystem"
    assert plan[1]["tool"] == "system"
