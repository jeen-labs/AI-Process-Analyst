# AI Process Analyst
# Module: tests.test_agent_registry
# Purpose: Test the AgentRegistry component of the enterprise orchestration layer.
# Phase: Milestone 3 - Enterprise AI Orchestration Layer
# Phase 3.7 - Agent Registry

from src.orchestration.agent_registry import (
AgentAlreadyRegisteredError,
AgentNotFoundError,
AgentRegistry,
)



class ExampleAgent:
    """Simple test agent used by the registry tests."""

    def execute(self, request):
        """Return a deterministic test response."""
        return {
            "agent": "example",
            "request": request,
        }


def test_agent_registry_initialises():
    """Registry should initialise with no registered agents."""
    registry = AgentRegistry()
    assert registry.list_agents() == []


def test_register_agent():
    """Registry should register an agent under a name."""
    registry = AgentRegistry()
    agent = ExampleAgent()
    registry.register("process_analysis", agent)
    assert registry.list_agents() == ["process_analysis"]


def test_register_agent_can_be_retrieved():
    """Registered agent should be retrievable by name."""
    registry = AgentRegistry()
    agent = ExampleAgent()
    registry.register("process_analysis", agent)
    retrieved = registry.get("process_analysis")
    assert retrieved is agent


def test_registry_contains_registered_agent():
    """Registry should report whether an agent is registered."""
    registry = AgentRegistry()
    registry.register("process_analysis", ExampleAgent())
    assert registry.contains("process_analysis") is True


def test_registry_does_not_contain_unknown_agent():
    """Registry should return False for an unknown agent."""
    registry = AgentRegistry()
    assert registry.contains("unknown") is False


def test_register_agent_rejects_empty_name():
    """Registry should reject an empty agent name."""
    registry = AgentRegistry()
    try:
        registry.register("", ExampleAgent())
        assert False
    except ValueError:
        assert True


def test_register_agent_rejects_whitespace_name():
    """Registry should reject a whitespace-only agent name."""
    registry = AgentRegistry()
    try:
        registry.register("   ", ExampleAgent())
        assert False
    except ValueError:
        assert True


def test_register_agent_rejects_none_agent():
    """Registry should reject a None agent."""
    registry = AgentRegistry()
    try:
        registry.register("process_analysis", None)
        assert False
    except ValueError:
        assert True


def test_registering_same_name_rejects_duplicate():
    """Registering an existing name should raise an error."""

    
    registry = AgentRegistry()

    first_agent = ExampleAgent()
    second_agent = ExampleAgent()

    registry.register("process_analysis", first_agent)

    try:
        registry.register("process_analysis", second_agent)
        assert False
    except AgentAlreadyRegisteredError:
        assert True

    assert registry.get("process_analysis") is first_agent
    



def test_register_multiple_agents():
    """Registry should support multiple named agents."""
    registry = AgentRegistry()
    registry.register("process_analysis", ExampleAgent())
    registry.register("document_analysis", ExampleAgent())
    assert registry.list_agents() == ["document_analysis", "process_analysis"]


def test_registry_preserves_agent_instance():
    """Registry should preserve the original agent instance."""
    registry = AgentRegistry()
    agent = ExampleAgent()
    registry.register("process_analysis", agent)
    assert registry.get("process_analysis") is agent


def test_registry_contains_returns_false_for_none():
    """Registry should return False for None."""
    registry = AgentRegistry()
    assert registry.contains(None) is False

def test_list_agents_is_sorted():
    """Agent names should be returned in deterministic order."""
    registry = AgentRegistry()
    registry.register("z_agent", ExampleAgent())
    registry.register("a_agent", ExampleAgent())
    registry.register("m_agent", ExampleAgent())
    assert registry.list_agents() == ["a_agent", "m_agent", "z_agent"]


def test_registered_agent_can_execute():
    """The registry should return an executable registered agent."""
    registry = AgentRegistry()
    agent = ExampleAgent()
    registry.register("process_analysis", agent)
    retrieved = registry.get("process_analysis")
    result = retrieved.execute("Analyse customer onboarding.")
    assert result == {
        "agent": "example",
        "request": "Analyse customer onboarding.",
    }


def test_registry_is_deterministic():
    """Repeated listing should return the same result."""
    registry = AgentRegistry()
    registry.register("process_analysis", ExampleAgent())
    first = registry.list_agents()
    second = registry.list_agents()
    assert first == second