"""
AI Process Analyst

Module:
tests.test_orchestration_governance_integration

Purpose:
Integration tests for the production orchestration governance path.

Phase:
Milestone 4 - Governance Platform
Phase 4.10 - Integrate Governance Platform with Orchestration

Architecture under test:

    OrchestrationEngine
            |
            v
    GovernedExecution
            |
            v
    GovernanceDecisionBoundary
            |
        +---+---+---+
        |   |   |   |
    Security  Compliance  Authorization
            |
            v
        GovernanceAudit
            |
            v
    ExecutionManager
            |
            v
        Registered Agent

Purpose of this test module:
- Verify that production orchestration uses GovernedExecution.
- Verify that GovernedExecution uses GovernanceDecisionBoundary.
- Verify that the actual governance decision is returned.
- Verify that governance is evaluated exactly once.
- Verify that security denial prevents execution.
- Verify that compliance denial prevents execution.
- Verify that authorization denial prevents execution.
- Verify that allowed decisions are audited exactly once.
- Verify that legacy Governance is not used when GovernedExecution
  is supplied.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest

from src.governance import (
    GovernanceAudit,
    GovernanceAuthorization,
    GovernanceCompliance,
    GovernanceDecisionBoundary,
    GovernancePermission,
    GovernancePermissions,
    GovernancePolicyEngine,
    GovernanceSecurity,
)
from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.execution_manager import ExecutionManager
from src.orchestration.governance import Governance
from src.orchestration.governed_execution import GovernedExecution
from src.orchestration.orchestration_engine import (
    OrchestrationEngine,
    OrchestrationEngineError,
)
from src.orchestration.planner import Planner


# =============================================================================
# Test Agent
# =============================================================================


class TrackingAgent:
    """
    Deterministic test agent used to verify execution behaviour.
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


# =============================================================================
# Governance Fixtures
# =============================================================================


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
            subject="orchestration",
            action="process_analysis",
            resource="process_analysis",
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
def decision_boundary(
    authorization: GovernanceAuthorization,
    audit: GovernanceAudit,
) -> GovernanceDecisionBoundary:
    return GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )


# =============================================================================
# Orchestration Fixtures
# =============================================================================


@pytest.fixture
def agent() -> TrackingAgent:
    return TrackingAgent()


@pytest.fixture
def registry(
    agent: TrackingAgent,
) -> AgentRegistry:
    registry = AgentRegistry()

    registry.register(
        "process_analysis",
        agent,
    )

    return registry


@pytest.fixture
def legacy_governance() -> Governance:
    return Governance()


@pytest.fixture
def execution_manager(
    registry: AgentRegistry,
    legacy_governance: Governance,
) -> ExecutionManager:
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


@pytest.fixture
def engine(
    registry: AgentRegistry,
    legacy_governance: Governance,
    execution_manager: ExecutionManager,
    governed_execution: GovernedExecution,
) -> OrchestrationEngine:
    return OrchestrationEngine(
        planner=Planner(),
        agent_registry=registry,
        governance=legacy_governance,
        execution_manager=execution_manager,
        governed_execution=governed_execution,
    )


# =============================================================================
# Authoritative Governance Path
# =============================================================================


def test_orchestration_uses_governed_execution(
    engine: OrchestrationEngine,
    governed_execution: GovernedExecution,
) -> None:
    """
    Production orchestration must use GovernedExecution when supplied.
    """

    governed_execution.execute_with_decision = Mock(
        wraps=governed_execution.execute_with_decision,
    )

    result = engine.orchestrate(
        "Analyse the customer onboarding process."
    )

    governed_execution.execute_with_decision.assert_called_once()

    assert result["governance"]["action"] == (
        "process_analysis"
    )

    assert result["governance"]["allowed"] is True


# =============================================================================
# Actual Governance Decision
# =============================================================================


def test_orchestration_returns_actual_governance_decision(
    engine: OrchestrationEngine,
) -> None:
    """
    The orchestration result must contain the actual governance decision
    returned by GovernanceDecisionBoundary.
    """

    result = engine.orchestrate(
        "Analyse the customer onboarding process."
    )

    assert result["governance"] == {
        "action": "process_analysis",
        "allowed": True,
        "reason": (
            "Action is authorized by governance policy and permissions."
        ),
    }


# =============================================================================
# Governance Evaluation Exactly Once
# =============================================================================


def test_orchestration_governance_evaluated_once(
    engine: OrchestrationEngine,
    decision_boundary: GovernanceDecisionBoundary,
) -> None:
    """
    A complete orchestration request must evaluate governance exactly once.
    """

    decision_boundary.evaluate = Mock(
        wraps=decision_boundary.evaluate,
    )

    engine.orchestrate(
        "Analyse the customer onboarding process."
    )

    decision_boundary.evaluate.assert_called_once()


# =============================================================================
# Security Denial
# =============================================================================


def test_security_denial_prevents_execution(
    registry: AgentRegistry,
    agent: TrackingAgent,
    execution_manager: ExecutionManager,
) -> None:
    """
    A security denial must prevent execution.
    """

    security = Mock(
        spec=GovernanceSecurity,
    )

    security.evaluate.return_value = {
        "action": "process_analysis",
        "allowed": False,
        "reason": "security validation failed",
    }

    audit = GovernanceAudit()

    boundary = GovernanceDecisionBoundary(
        security=security,
        compliance=GovernanceCompliance(),
        authorization=Mock(
            spec=GovernanceAuthorization,
        ),
        audit=audit,
    )

    governed_execution = GovernedExecution(
        decision_boundary=boundary,
        execution_manager=execution_manager,
    )

    engine = OrchestrationEngine(
        planner=Planner(),
        agent_registry=registry,
        governance=Governance(),
        execution_manager=execution_manager,
        governed_execution=governed_execution,
    )

    with pytest.raises(
        OrchestrationEngineError,
        match="security validation failed",
    ):
        engine.orchestrate(
            "Analyse the customer onboarding process."
        )

    assert agent.calls == []


# =============================================================================
# Compliance Denial
# =============================================================================


def test_compliance_denial_prevents_execution(
    registry: AgentRegistry,
    agent: TrackingAgent,
    execution_manager: ExecutionManager,
) -> None:
    """
    A compliance denial must prevent execution.
    """

    compliance = Mock(
        spec=GovernanceCompliance,
    )

    compliance.evaluate.return_value = {
        "action": "process_analysis",
        "allowed": False,
        "reason": "compliance requirement failed",
    }

    audit = GovernanceAudit()

    boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=compliance,
        authorization=Mock(
            spec=GovernanceAuthorization,
        ),
        audit=audit,
    )

    governed_execution = GovernedExecution(
        decision_boundary=boundary,
        execution_manager=execution_manager,
    )

    engine = OrchestrationEngine(
        planner=Planner(),
        agent_registry=registry,
        governance=Governance(),
        execution_manager=execution_manager,
        governed_execution=governed_execution,
    )

    with pytest.raises(
        OrchestrationEngineError,
        match="compliance requirement failed",
    ):
        engine.orchestrate(
            "Analyse the customer onboarding process."
        )

    assert agent.calls == []


# =============================================================================
# Authorization Denial
# =============================================================================


def test_authorization_denial_prevents_execution(
    registry: AgentRegistry,
    agent: TrackingAgent,
    execution_manager: ExecutionManager,
) -> None:
    """
    An authorization denial must prevent execution.
    """

    authorization = Mock(
        spec=GovernanceAuthorization,
    )

    authorization.authorize.return_value = {
        "action": "process_analysis",
        "allowed": False,
        "reason": (
            "Subject does not have the required permission."
        ),
    }

    audit = GovernanceAudit()

    boundary = GovernanceDecisionBoundary(
        security=GovernanceSecurity(),
        compliance=GovernanceCompliance(),
        authorization=authorization,
        audit=audit,
    )

    governed_execution = GovernedExecution(
        decision_boundary=boundary,
        execution_manager=execution_manager,
    )

    engine = OrchestrationEngine(
        planner=Planner(),
        agent_registry=registry,
        governance=Governance(),
        execution_manager=execution_manager,
        governed_execution=governed_execution,
    )

    with pytest.raises(
        OrchestrationEngineError,
        match="Subject does not have the required permission",
    ):
        engine.orchestrate(
            "Analyse the customer onboarding process."
        )

    assert agent.calls == []


# =============================================================================
# Audit
# =============================================================================


def test_allowed_governance_decision_is_audited(
    engine: OrchestrationEngine,
    audit: GovernanceAudit,
) -> None:
    """
    An allowed orchestration request must produce exactly one audit entry.
    """

    engine.orchestrate(
        "Analyse the customer onboarding process."
    )

    assert audit.count() == 1

    entry = audit.entries()[0]

    assert entry.action == "process_analysis"
    assert entry.allowed is True


# =============================================================================
# Decision Boundary Is Authoritative
# =============================================================================


def test_legacy_governance_is_not_used_when_governed_execution_is_present(
    registry: AgentRegistry,
    execution_manager: ExecutionManager,
    governed_execution: GovernedExecution,
) -> None:
    """
    When GovernedExecution is supplied, the legacy Governance object must
    not participate in orchestration execution.
    """

    legacy_governance = Mock(
        spec=Governance,
    )

    engine = OrchestrationEngine(
        planner=Planner(),
        agent_registry=registry,
        governance=legacy_governance,
        execution_manager=execution_manager,
        governed_execution=governed_execution,
    )

    result = engine.orchestrate(
        "Analyse the customer onboarding process."
    )

    assert result["governance"]["allowed"] is True

    legacy_governance.is_allowed.assert_not_called()