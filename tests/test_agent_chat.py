import unittest
from unittest.mock import MagicMock
from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat
from agents.agent_chat import setup_agent_chat
from agents.address_agents import RETRIEVER, REPORT_AGENT

class TestAgentChat(unittest.TestCase):
    def setUp(self):
        self.kernel = MagicMock(spec=Kernel)

    def test_setup_agent_chat_returns_agent_group_chat(self):
        chat = setup_agent_chat(self.kernel)
        self.assertIsInstance(chat, AgentGroupChat)

    def test_agent_group_chat_contains_agents(self):
        chat = setup_agent_chat(self.kernel)
        agent_names = [agent.name for agent in chat.agents]
        self.assertIn(RETRIEVER, agent_names)
        self.assertIn(REPORT_AGENT, agent_names)

    def test_agent_selection_strategy_is_configured(self):
        chat = setup_agent_chat(self.kernel)
        self.assertIsNotNone(chat.selection_strategy)
        self.assertEqual(chat.selection_strategy.initial_agent.name, RETRIEVER)

if __name__ == "__main__":
    unittest.main()
