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
- Governance request construction
- GovernanceDecisionBoundary integration
- Security integration
- Compliance integration
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
- Audit ordering
- Governance failure handling
"""

from typing import Any
from unittest.mock import Mock

import pytest

from src.governance.governance_audit import GovernanceAudit
from src.governance.governance_authorization import (
    GovernanceAuthorization,
)
from src.governance.governance_compliance import (
    GovernanceCompliance,
)
from src.governance.governance_contracts import (
    GovernanceDecision,
    GovernanceRequest,
)
from src.governance.governance_decision_boundary import (
    GovernanceDecisionBoundary,
)
from src.governance.governance_permissions import (
    GovernancePermission,
    GovernancePermissions,
)
from src.governance.governance_policy_engine import (
    GovernancePolicyEngine,
)
from src.governance.governance_security import (
    GovernanceSecurity,
)
from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.execution_manager import ExecutionManager
from src.orchestration.governance import Governance
from src.orchestration.governed_execution import (
    GovernedExecution,
    GovernedExecutionError,
)


# =============================================================================
# Test Agents
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

    pass


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
def security() -> GovernanceSecurity:
    return GovernanceSecurity()


@pytest.fixture
def compliance() -> GovernanceCompliance:
    return GovernanceCompliance()


@pytest.fixture
def audit() -> GovernanceAudit:
    return GovernanceAudit()


@pytest.fixture
def decision_boundary(
    security: GovernanceSecurity,
    compliance: GovernanceCompliance,
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
) -> GovernanceDecisionBoundary:
    return GovernanceDecisionBoundary(
        security=security,
        compliance=compliance,
        authorization=authorization,
        audit=audit,
    )


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
    decision_boundary: GovernanceDecisionBoundary,
    execution_manager: ExecutionManager,
) -> GovernedExecution:
    return GovernedExecution(
        decision_boundary=decision_boundary,
        execution_manager=execution_manager,
    )


# =============================================================================
# Initialisation
# =============================================================================


def test_governed_execution_initialises(
    governed_execution: GovernedExecution,
):
    """
    GovernedExecution should initialise with valid dependencies.
    """

    assert isinstance(
        governed_execution,
        GovernedExecution,
    )


def test_governed_execution_rejects_none_decision_boundary(
    execution_manager: ExecutionManager,
):
    """
    Decision boundary dependency must not be None.
    """

    with pytest.raises(
        GovernedExecutionError,
        match="decision_boundary must not be None",
    ):
        GovernedExecution(
            decision_boundary=None,
            execution_manager=execution_manager,
        )


def test_governed_execution_rejects_none_execution_manager(
    decision_boundary: GovernanceDecisionBoundary,
):
    """
    Execution manager dependency must not be None.
    """

    with pytest.raises(
        GovernedExecutionError,
        match="execution_manager must not be None",
    ):
        GovernedExecution(
            decision_boundary=decision_boundary,
            execution_manager=None,
        )


# =============================================================================
# Successful Governed Execution
# =============================================================================


def test_governed_execution_authorizes_and_executes(
    governed_execution: GovernedExecution,
    agent: ExampleAgent,
):
    """
    Authorized requests should execute the registered agent.
    """

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
    """
    Allowed governance decisions should be audited.
    """

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
    """
    The original request object should reach the agent unchanged.
    """

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
    """
    Policy denial must prevent execution.
    """

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

    decision_boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=legacy_governance,
    )

    governed_execution = GovernedExecution(
        decision_boundary=decision_boundary,
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
    """
    Missing subject permission must prevent execution.
    """

    registry.register(
        "process_analysis",
        agent,
    )

    permissions = GovernancePermissions()

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    decision_boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=legacy_governance,
    )

    governed_execution = GovernedExecution(
        decision_boundary=decision_boundary,
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
    decision_boundary: GovernanceDecisionBoundary,
    audit: GovernanceAudit,
):
    """
    A denied governance decision must prevent the execution
    manager from being called.
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

    policy_engine = GovernancePolicyEngine(
        allowed_actions=set()
    )

    permissions = GovernancePermissions()

    authorization = GovernanceAuthorization(
        policy_engine=policy_engine,
        permissions=permissions,
    )

    denied_boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )

    execution_manager = TrackingExecutionManager()

    governed_execution = GovernedExecution(
        decision_boundary=denied_boundary,
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
    """
    authorize() should not execute the agent.
    """

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
    """
    authorize() should return False when policy denies the action.
    """

    authorization = GovernanceAuthorization(
        policy_engine=GovernancePolicyEngine(
            allowed_actions=set()
        ),
        permissions=GovernancePermissions(),
    )

    decision_boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )

    governed_execution = GovernedExecution(
        decision_boundary=decision_boundary,
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
    """
    Action must be a non-empty string.
    """

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
    """
    Empty actions must be rejected.
    """

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
    """
    Subject must be a non-empty string.
    """

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
    """
    Empty subject must be rejected.
    """

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
    """
    Resource must be a non-empty string.
    """

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
    """
    Empty resource must be rejected.
    """

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
    """
    Context must be a dictionary when supplied.
    """

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
    """
    Action, subject, and resource should be stripped.
    """

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
    """
    Governed execution should accept additional context.
    """

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
    """
    The caller's context dictionary should remain unchanged.
    """

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
# Security Boundary
# =============================================================================


def test_governed_execution_uses_security_boundary(
    audit: GovernanceAudit,
    execution_manager: ExecutionManager,
):
    """
    Invalid governance requests must fail through the security
    boundary before execution.
    """

    authorization = GovernanceAuthorization(
        policy_engine=GovernancePolicyEngine(
            allowed_actions={
                "process_analysis",
            }
        ),
        permissions=GovernancePermissions(),
    )

    decision_boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )

    governed_execution = GovernedExecution(
        decision_boundary=decision_boundary,
        execution_manager=execution_manager,
    )

    with pytest.raises(
        GovernedExecutionError,
        match="action must not be empty",
    ):
        governed_execution.execute(
            action="   ",
            request="Analyse onboarding.",
            subject="analyst",
            resource="customer_onboarding",
        )


# =============================================================================
# Compliance Boundary
# =============================================================================


def test_governed_execution_uses_compliance_boundary(
    audit: GovernanceAudit,
    execution_manager: ExecutionManager,
):
    """
    The governed execution boundary must use the compliance
    stage through GovernanceDecisionBoundary.
    """

    class TrackingCompliance(GovernanceCompliance):
        def __init__(self):
            self.calls = 0

        def evaluate(
            self,
            request: GovernanceRequest,
        ) -> GovernanceDecision:
            self.calls += 1

            return GovernanceDecision(
                action=request["action"],
                allowed=False,
                reason="Compliance test denial.",
            )

    compliance = TrackingCompliance()

    authorization = GovernanceAuthorization(
        policy_engine=GovernancePolicyEngine(
            allowed_actions={
                "process_analysis",
            }
        ),
        permissions=GovernancePermissions(),
    )

    decision_boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=compliance,
        authorization=authorization,
        audit=audit,
    )

    governed_execution = GovernedExecution(
        decision_boundary=decision_boundary,
        execution_manager=execution_manager,
    )

    with pytest.raises(
        GovernedExecutionError,
        match="Compliance test denial",
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject="analyst",
            resource="customer_onboarding",
        )

    assert compliance.calls == 1

    assert audit.count() == 1

    assert audit.entries()[0].allowed is False


# =============================================================================
# Non-Executable Agent
# =============================================================================


def test_governed_execution_rejects_non_executable_agent(
    registry: AgentRegistry,
    legacy_governance: Governance,
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
):
    """
    Authorization should succeed but execution should fail.
    """

    registry.register(
        "process_analysis",
        NonExecutableAgent(),
    )

    decision_boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=legacy_governance,
    )

    governed_execution = GovernedExecution(
        decision_boundary=decision_boundary,
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

    # Governance happened and was audited even though execution failed.
    assert audit.count() == 1

    assert audit.entries()[0].allowed is True


# =============================================================================
# Determinism
# =============================================================================


def test_governed_execution_is_deterministic(
    governed_execution: GovernedExecution,
    audit: GovernanceAudit,
):
    """
    Repeated governed execution should be deterministic.
    """

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
    The governance decision must be audited before the agent executes.
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

    decision_boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )

    execution_manager = ExecutionManager(
        agent_registry=registry,
        governance=Governance(),
    )

    governed_execution = GovernedExecution(
        decision_boundary=decision_boundary,
        execution_manager=execution_manager,
    )

    governed_execution.execute(
        action="process_analysis",
        request="Analyse onboarding.",
        subject="analyst",
        resource="customer_onboarding",
    )

    assert agent.audit_count_at_execution == 1


# =============================================================================
# Governance Decision Boundary Failure
# =============================================================================


def test_governed_execution_rejects_invalid_governance_decision(
    execution_manager: ExecutionManager,
):
    """
    GovernedExecution must fail closed when the decision boundary
    returns an invalid decision.
    """

    class InvalidDecisionBoundary:
        def evaluate(
            self,
            request: GovernanceRequest,
        ):
            return {
                "action": request["action"],
            }

    governed_execution = GovernedExecution(
        decision_boundary=InvalidDecisionBoundary(),
        execution_manager=execution_manager,
    )

    with pytest.raises(
        GovernedExecutionError,
        match="Governance decision boundary returned an invalid decision",
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject="analyst",
            resource="customer_onboarding",
        )


def test_governed_execution_handles_decision_boundary_failure(
    execution_manager: ExecutionManager,
):
    """
    GovernedExecution must convert decision-boundary failures into
    GovernedExecutionError.
    """

    class FailingDecisionBoundary:
        def evaluate(
            self,
            request: GovernanceRequest,
        ):
            raise RuntimeError(
                "simulated governance failure"
            )

    governed_execution = GovernedExecution(
        decision_boundary=FailingDecisionBoundary(),
        execution_manager=execution_manager,
    )

    with pytest.raises(
        GovernedExecutionError,
        match="Governance decision boundary failed",
    ):
        governed_execution.execute(
            action="process_analysis",
            request="Analyse onboarding.",
            subject="analyst",
            resource="customer_onboarding",
        )

# =============================================================================
# Decision-Preserving Execution
# =============================================================================


def test_execute_with_decision_returns_actual_governance_decision(
    governed_execution: GovernedExecution,
) -> None:
    """
    execute_with_decision() must return the actual governance decision
    together with the execution result.
    """

    decision, result = governed_execution.execute_with_decision(
        action="process_analysis",
        request="Analyse customer onboarding.",
        subject="analyst",
        resource="customer_onboarding",
    )

    assert decision == {
        "action": "process_analysis",
        "allowed": True,
        "reason": (
            "Action is authorized by governance policy and permissions."
        ),
    }

    assert result == {
        "agent": "process_analysis",
        "request": "Analyse customer onboarding.",
        "status": "executed",
    }


def test_execute_delegates_to_execute_with_decision(
    governed_execution: GovernedExecution,
) -> None:
    """
    Existing execute() must preserve its result-only API.
    """

    governed_execution.execute_with_decision = Mock(
        return_value=(
            {
                "action": "process_analysis",
                "allowed": True,
                "reason": "Action permitted.",
            },
            {
                "agent": "process_analysis",
                "request": "Analyse customer onboarding.",
                "status": "executed",
            },
        )
    )

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

    governed_execution.execute_with_decision.assert_called_once()


def test_execute_with_decision_does_not_execute_when_denied(
    audit: GovernanceAudit,
    execution_manager: ExecutionManager,
) -> None:
    """
    A denied governance decision must prevent execution.
    """

    authorization = GovernanceAuthorization(
        policy_engine=GovernancePolicyEngine(
            allowed_actions=set(),
        ),
        permissions=GovernancePermissions(),
    )

    boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )

    execution_manager.execute = Mock(
        wraps=execution_manager.execute,
    )

    governed_execution = GovernedExecution(
        decision_boundary=boundary,
        execution_manager=execution_manager,
    )

    with pytest.raises(
        GovernedExecutionError,
        match="Action is denied by governance policy",
    ):
        governed_execution.execute_with_decision(
            action="process_analysis",
            request="Analyse customer onboarding.",
            subject="analyst",
            resource="customer_onboarding",
        )

    execution_manager.execute.assert_not_called()