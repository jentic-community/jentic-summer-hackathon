class BaseCommunicationAgent:
    def __init__(self):
        pass

    def test_connection(self) -> bool:
        raise NotImplementedError

    def send_message(self, recipient: str, message: str) -> dict:
        raise NotImplementedError

    def process_agent_query(self, query: str, user_context: dict) -> str:
        raise NotImplementedError


