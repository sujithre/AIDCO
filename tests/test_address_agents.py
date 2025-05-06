import unittest
from unittest.mock import MagicMock
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from agents.address_agents import create_address_agents, RETRIEVER, REPORT_AGENT

class TestAddressAgents(unittest.TestCase):
    def setUp(self):
        self.kernel = MagicMock(spec=Kernel)

    def test_create_address_agents_returns_two_agents(self):
        retriever_agent, report_agent = create_address_agents(self.kernel)
        self.assertIsInstance(retriever_agent, ChatCompletionAgent)
        self.assertIsInstance(report_agent, ChatCompletionAgent)

    def test_agents_have_correct_names(self):
        retriever_agent, report_agent = create_address_agents(self.kernel)
        self.assertEqual(retriever_agent.name, RETRIEVER)
        self.assertEqual(report_agent.name, REPORT_AGENT)

    def test_agents_have_correct_plugins(self):
        retriever_agent, report_agent = create_address_agents(self.kernel)
        self.assertIn("telsearch", retriever_agent.plugins)
        self.assertIn("report", report_agent.plugins)

if __name__ == "__main__":
    unittest.main()
