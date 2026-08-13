"""
AI Process Analyst

Module:
tests.test_governed_execution

Purpose:
Unit tests for the Phase 4.6A GovernedExecution boundary.

Phase:
Milestone 4 - Governance Platform
Phase 4.6A - Governed Execution Boundary

Coverage:
- Dependency validation
- Governance request validation
- Authorization integration
- Permission integration
- Policy integration
- Audit integration
- Execution integration
- Denied execution safety
- Authorization-only behaviour
- Request preservation
- Context handling
- Deterministic behaviour
"""

from typing import Any

import pytest

from src.governance.governance_audit import GovernanceAudit
from src.governance.governance_authorization import (
    GovernanceAuthorization,
)
from src.governance.governance_permissions import (
    GovernancePermission,
    GovernancePermissions,
)
from src.governance.governance_policy_engine import (
    GovernancePolicyEngine,
)
from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.execution_manager import ExecutionManager
from src.orchestration.governance import Governance
from src.orchestration.governed_execution import (
    GovernedExecution,
    GovernedExecutionError,
)


# =============================================================================
# Test Agent
# =============================================================================


class ExampleAgent:
    """
    Deterministic test agent.
    """

    def __init__(self) -> None:
        self.calls: list[Any] = []

    def execute(
        self,
        request: Any,
    ) -> dict[str, Any]:
        self.calls.append(request)

        return {
            "agent": "process_analysis",
            "request": request,
            "status": "executed",
        }


class NonExecutableAgent:
    """
    Registered object without an execute method.
    """


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def registry() -> AgentRegistry:
    return AgentRegistry()


@pytest.fixture
def legacy_governance() -> Governance:
    return Governance()


@pytest.fixture
def policy_engine() -> GovernancePolicyEngine:
    return GovernancePolicyEngine(
        allowed_actions={
            "process_analysis",
        }
    )


@pytest.fixture
def permissions() -> GovernancePermissions:
    permissions = GovernancePermissions()

    permissions.grant(
        GovernancePermission(
            subject="analyst",
            action="process_analysis",
            resource="customer_onboarding",
        )
    )

    return permissions


@pytest.fixture
def authorization(
    policy_engine: GovernancePolicyEngine,
    permissions: GovernancePermissions,
) -> GovernanceAuthorization:
    return GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )


@pytest.fixture
def audit() -> GovernanceAudit:
    return GovernanceAudit()


@pytest.fixture
def agent() -> ExampleAgent:
    return ExampleAgent()


@pytest.fixture
def execution_manager(
    registry: AgentRegistry,
    legacy_governance: Governance,
    agent: ExampleAgent,
) -> ExecutionManager:
    registry.register(
        "process_analysis",
        agent,
    )

    return ExecutionManager(
        agent_registry=registry,
        governance=legacy_governance,
    )


@pytest.fixture
def governed_execution(
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
    execution_manager: ExecutionManager,
) -> GovernedExecution:
    return GovernedExecution(
        authorization=authorization,
        audit=audit,
        execution_manager=execution_manager,
    )


# =============================================================================
# Initialisation
# =============================================================================


def test_governed_execution_initialises(
    governed_execution: GovernedExecution,
):
    """GovernedExecution should initialise with valid dependencies."""

    assert isinstance(
        governed_execution,
        GovernedExecution,
    )


def test_governed_execution_rejects_none_authorization(
    audit: GovernanceAudit,
    execution_manager: ExecutionManager,
):
    """Authorization dependency must not be None."""

    with pytest.raises(
        GovernedExecutionError,
        match="authorization must not be None",
    ):
        GovernedExecution(
            authorization=None,
            audit=audit,
            execution_manager=execution_manager,
        )


def test_governed_execution_rejects_none_audit(
    authorization: GovernanceAuthorization,
    execution_manager: ExecutionManager,
):
    """Audit dependency must not be None."""

    with pytest.raises(
        GovernedExecutionError,
        match="audit must not be None",
    ):
        GovernedExecution(
            authorization=authorization,
            audit=None,
            execution_manager=execution_manager,
        )


def test_governed_execution_rejects_none_execution_manager(
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
):
    """Execution manager dependency must not be None."""

    with pytest.raises(
        GovernedExecutionError,
        match="execution_manager must not be None",
    ):
        GovernedExecution(
            authorization=authorization,
            audit=audit,
            execution_manager=None,
        )


# =============================================================================
# Successful Governed Execution
# =============================================================================


def test_governed_execution_authorizes_and_executes(
    governed_execution: GovernedExecution,
    agent: ExampleAgent,
):
    """Authorized requests should execute the registered agent."""

    result = governed_execution.execute(
        action="process_analysis",
        request="Analyse customer onboarding.",
        subject="analyst",
        resource="customer_onboarding",
    )

    assert result == {
        "agent": "process_analysis",
        "request": "Analyse customer onboarding.",
        "status": "executed",
    }

    assert agent.calls == [
        "Analyse customer onboarding.",
    ]


def test_governed_execution_records_allowed_decision(
    governed_execution: GovernedExecution,
    audit: GovernanceAudit,
):
    """Allowed authorization decisions should be audited."""

    governed_execution.execute(
        action="process_analysis",
        request="Analyse customer onboarding.",
        subject="analyst",
        resource="customer_onboarding",
    )

    assert audit.count() == 1

    assert audit.entries()[0].action == (
        "process_analysis"
    )

    assert audit.entries()[0].allowed is True

    assert audit.entries()[0].reason == (
        "Action is authorized by governance policy and permissions."
    )


def test_governed_execution_preserves_request(
    governed_execution: GovernedExecution,
):
    """The original request object should reach the agent unchanged."""

    request = {
        "document": "customer onboarding",
        "priority": "high",
    }

    result = governed_execution.execute(
        action="process_analysis",
        request=request,
        subject="analyst",
        resource="customer_onboarding",
    )

    assert result["request"] is request


# =============================================================================
# Policy Denial
# =============================================================================


def test_governed_execution_denies_policy_blocked_action(
    registry: AgentRegistry,
    legacy_governance: Governance,
    audit: GovernanceAudit,
    permissions: GovernancePermissions,
    agent: ExampleAgent,
):
    """Policy denial must prevent execution."""

    registry.register(
        "process_analysis",
        agent,
    )

    policy_engine = GovernancePolicyEngine(
        allowed_actions=set()
    )

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=legacy_governance,
    )

    governed_execution = GovernedExecution(
        authorization=authorization,
        audit=audit,
        execution_manager=execution_manager,
    )

    with pytest.raises(
        GovernedExecutionError,
        match="Action is denied by governance policy",
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject="analyst",
            resource="customer_onboarding",
        )

    assert agent.calls == []

    assert audit.count() == 1

    assert audit.entries()[0].allowed is False


# =============================================================================
# Permission Denial
# =============================================================================


def test_governed_execution_denies_missing_permission(
    registry: AgentRegistry,
    legacy_governance: Governance,
    audit: GovernanceAudit,
    policy_engine: GovernancePolicyEngine,
    agent: ExampleAgent,
):
    """Missing subject permission must prevent execution."""

    registry.register(
        "process_analysis",
        agent,
    )

    permissions = GovernancePermissions()

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=legacy_governance,
    )

    governed_execution = GovernedExecution(
        authorization=authorization,
        audit=audit,
        execution_manager=execution_manager,
    )

    with pytest.raises(
        GovernedExecutionError,
        match="Subject does not have the required permission",
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject="unauthorized-user",
            resource="customer_onboarding",
        )

    assert agent.calls == []

    assert audit.count() == 1

    assert audit.entries()[0].allowed is False


# =============================================================================
# Safety / Non-Execution
# =============================================================================


def test_denied_action_never_reaches_execution_manager(
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
):
    """
    A denied authorization must prevent the execution manager
    from being called.
    """

    class TrackingExecutionManager:
        def __init__(self):
            self.calls = []

        def execute(
            self,
            action,
            request,
        ):
            self.calls.append(
                (action, request)
            )

            return request

    permissions = GovernancePermissions()

    authorization = GovernanceAuthorization(
        policy_engine=GovernancePolicyEngine(
            allowed_actions=set()
        ),
        permissions=permissions,
    )

    execution_manager = TrackingExecutionManager()

    governed_execution = GovernedExecution(
        authorization=authorization,
        audit=audit,
        execution_manager=execution_manager,
    )

    with pytest.raises(
        GovernedExecutionError,
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject="analyst",
            resource="customer_onboarding",
        )

    assert execution_manager.calls == []


# =============================================================================
# Authorization Only
# =============================================================================


def test_authorize_returns_true_without_execution(
    governed_execution: GovernedExecution,
    agent: ExampleAgent,
    audit: GovernanceAudit,
):
    """authorize() should not execute the agent."""

    result = governed_execution.authorize(
        action="process_analysis",
        subject="analyst",
        resource="customer_onboarding",
    )

    assert result is True

    assert agent.calls == []

    assert audit.count() == 1


def test_authorize_returns_false_for_policy_denial(
    audit: GovernanceAudit,
    execution_manager: ExecutionManager,
):
    """authorize() should return False when policy denies the action."""

    authorization = GovernanceAuthorization(
        policy_engine=GovernancePolicyEngine(
            allowed_actions=set()
        ),
        permissions=GovernancePermissions(),
    )

    governed_execution = GovernedExecution(
        authorization=authorization,
        audit=audit,
        execution_manager=execution_manager,
    )

    result = governed_execution.authorize(
        action="process_analysis",
        subject="analyst",
        resource="customer_onboarding",
    )

    assert result is False

    assert audit.count() == 1

    assert audit.entries()[0].allowed is False


# =============================================================================
# Input Validation
# =============================================================================


@pytest.mark.parametrize(
    "action",
    [
        None,
        123,
        [],
    ],
)
def test_governed_execution_rejects_invalid_action(
    governed_execution: GovernedExecution,
    action,
):
    """Action must be a non-empty string."""

    with pytest.raises(
        GovernedExecutionError,
        match="action must be a string",
    ):
        governed_execution.execute(
            action=action,
            request="Analyse onboarding.",
            subject="analyst",
            resource="customer_onboarding",
        )


@pytest.mark.parametrize(
    "action",
    [
        "",
        "   ",
    ],
)
def test_governed_execution_rejects_empty_action(
    governed_execution: GovernedExecution,
    action: str,
):
    """Empty actions must be rejected."""

    with pytest.raises(
        GovernedExecutionError,
        match="action must not be empty",
    ):
        governed_execution.execute(
            action=action,
            request="Analyse onboarding.",
            subject="analyst",
            resource="customer_onboarding",
        )


def test_governed_execution_rejects_invalid_subject(
    governed_execution: GovernedExecution,
):
    """Subject must be a non-empty string."""

    with pytest.raises(
        GovernedExecutionError,
        match="subject must be a string",
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject=None,
            resource="customer_onboarding",
        )


def test_governed_execution_rejects_empty_subject(
    governed_execution: GovernedExecution,
):
    """Empty subject must be rejected."""

    with pytest.raises(
        GovernedExecutionError,
        match="subject must not be empty",
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject="   ",
            resource="customer_onboarding",
        )


def test_governed_execution_rejects_invalid_resource(
    governed_execution: GovernedExecution,
):
    """Resource must be a non-empty string."""

    with pytest.raises(
        GovernedExecutionError,
        match="resource must be a string",
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject="analyst",
            resource=None,
        )


def test_governed_execution_rejects_empty_resource(
    governed_execution: GovernedExecution,
):
    """Empty resource must be rejected."""

    with pytest.raises(
        GovernedExecutionError,
        match="resource must not be empty",
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject="analyst",
            resource="   ",
        )


def test_governed_execution_rejects_invalid_context(
    governed_execution: GovernedExecution,
):
    """Context must be a dictionary when supplied."""

    with pytest.raises(
        GovernedExecutionError,
        match="context must be a dictionary",
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject="analyst",
            resource="customer_onboarding",
            context="invalid",
        )


# =============================================================================
# Normalisation
# =============================================================================


def test_governed_execution_normalises_governance_fields(
    governed_execution: GovernedExecution,
    audit: GovernanceAudit,
):
    """Action, subject, and resource should be stripped."""

    governed_execution.execute(
        action="  process_analysis  ",
        request="Analyse onboarding.",
        subject="  analyst  ",
        resource="  customer_onboarding  ",
    )

    entry = audit.entries()[0]

    assert entry.action == "process_analysis"


# =============================================================================
# Context
# =============================================================================


def test_governed_execution_accepts_context(
    governed_execution: GovernedExecution,
    audit: GovernanceAudit,
):
    """Governed execution should accept additional context."""

    result = governed_execution.execute(
        action="process_analysis",
        request="Analyse onboarding.",
        subject="analyst",
        resource="customer_onboarding",
        context={
            "source": "test",
            "priority": "high",
        },
    )

    assert result["status"] == "executed"

    assert audit.count() == 1


def test_governed_execution_does_not_mutate_context(
    governed_execution: GovernedExecution,
):
    """The caller's context dictionary should remain unchanged."""

    context = {
        "source": "test",
        "priority": "high",
    }

    governed_execution.execute(
        action="process_analysis",
        request="Analyse onboarding.",
        subject="analyst",
        resource="customer_onboarding",
        context=context,
    )

    assert context == {
        "source": "test",
        "priority": "high",
    }


# =============================================================================
# Non-Executable Agent
# =============================================================================


def test_governed_execution_rejects_non_executable_agent(
    registry: AgentRegistry,
    legacy_governance: Governance,
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
):
    """Authorization should succeed but execution should fail."""

    registry.register(
        "process_analysis",
        NonExecutableAgent(),
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=legacy_governance,
    )

    governed_execution = GovernedExecution(
        authorization=authorization,
        audit=audit,
        execution_manager=execution_manager,
    )

    with pytest.raises(
        GovernedExecutionError,
        match="Governed execution failed",
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject="analyst",
            resource="customer_onboarding",
        )

    # Authorization happened and was audited even though execution failed.
    assert audit.count() == 1

    assert audit.entries()[0].allowed is True


# =============================================================================
# Determinism
# =============================================================================


def test_governed_execution_is_deterministic(
    governed_execution: GovernedExecution,
    audit: GovernanceAudit,
):
    """Repeated governed execution should be deterministic."""

    first = governed_execution.execute(
        action="process_analysis",
        request="Analyse onboarding.",
        subject="analyst",
        resource="customer_onboarding",
    )

    second = governed_execution.execute(
        action="process_analysis",
        request="Analyse onboarding.",
        subject="analyst",
        resource="customer_onboarding",
    )

    assert first == second

    assert audit.count() == 2

    assert [
        entry.allowed
        for entry in audit.entries()
    ] == [
        True,
        True,
    ]


# =============================================================================
# Audit Ordering
# =============================================================================


def test_governed_execution_audits_before_execution(
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
):
    """
    The authorization decision must be audited before the agent executes.
    """

    class TrackingAgent:
        def __init__(self):
            self.audit_count_at_execution = None

        def execute(self, request):
            self.audit_count_at_execution = audit.count()

            return {
                "request": request,
            }

    registry = AgentRegistry()

    agent = TrackingAgent()

    registry.register(
        "process_analysis",
        agent,
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=Governance(),
    )

    governed_execution = GovernedExecution(
        authorization=authorization,
        audit=audit,
        execution_manager=execution_manager,
    )

    governed_execution.execute(
        action="process_analysis",
        request="Analyse onboarding.",
        subject="analyst",
        resource="customer_onboarding",
    )

    assert agent.audit_count_at_execution == 1