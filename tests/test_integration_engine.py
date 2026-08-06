from src.canonical_normalizer import CanonicalNormalizer
from src.enrichment import CanonicalEnricher
from src.integration import IntegrationEngine
from src.knowledge_graph import GraphBuilder
from src.normalizers import GeminiNormalizer
from src.ontology import OntologyEngine
from src.rules import RuleEngine
from src.validator import SchemaValidator


def test_integration_pipeline():

    normalizer = CanonicalNormalizer()
    normalizer.register_provider(
        "gemini",
        GeminiNormalizer(),
    )

    engine = IntegrationEngine(
        normalizer=normalizer,
        validator=SchemaValidator(),
        ontology=OntologyEngine(),
        enricher=CanonicalEnricher(),
        rules=RuleEngine(),
        graph_builder=GraphBuilder(),
    )

    provider_response = {
        "process": {
            "id": "PROC-001",
            "name": "Invoice Approval",
        }
    }

    result = engine.process(
        "gemini",
        provider_response,
    )

    assert result.validation_passed

    assert result.canonical_model is not None

    assert result.knowledge_graph is not None