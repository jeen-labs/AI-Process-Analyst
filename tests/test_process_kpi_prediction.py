"""
Tests for Phase 5.6 - KPI Prediction.
"""

import pytest

from src.process_intelligence.process_kpi_prediction import (
    KpiPrediction,
    ProcessKpiPredictionError,
    ProcessKpiPredictionResult,
    ProcessKpiPredictor,
    predict_kpi,
    predict_kpis,
)


# =============================================================================
# KpiPrediction
# =============================================================================


def test_kpi_prediction_is_immutable():
    prediction = KpiPrediction(
        kpi_name="Cycle Time",
        predicted_value=10.0,
        historical_average=10.0,
        observation_count=3,
        confidence=0.5,
    )

    with pytest.raises(AttributeError):
        prediction.predicted_value = 20.0


def test_kpi_prediction_to_dict():
    prediction = KpiPrediction(
        kpi_name="Cycle Time",
        predicted_value=10.0,
        historical_average=10.0,
        observation_count=3,
        confidence=0.5,
    )

    assert prediction.to_dict() == {
        "kpi_name": "Cycle Time",
        "predicted_value": 10.0,
        "historical_average": 10.0,
        "observation_count": 3,
        "confidence": 0.5,
        "method": "historical_mean",
    }


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "kpi_name": "",
            "predicted_value": 10.0,
            "historical_average": 10.0,
            "observation_count": 3,
            "confidence": 0.5,
        },
        {
            "kpi_name": "Cycle Time",
            "predicted_value": 10.0,
            "historical_average": 10.0,
            "observation_count": 0,
            "confidence": 0.5,
        },
        {
            "kpi_name": "Cycle Time",
            "predicted_value": 10.0,
            "historical_average": 10.0,
            "observation_count": 3,
            "confidence": 1.5,
        },
    ],
)
def test_kpi_prediction_rejects_invalid_values(kwargs):
    with pytest.raises(ProcessKpiPredictionError):
        KpiPrediction(**kwargs)


# =============================================================================
# ProcessKpiPredictionResult
# =============================================================================


def test_prediction_result_is_immutable():
    prediction = KpiPrediction(
        kpi_name="Cycle Time",
        predicted_value=10.0,
        historical_average=10.0,
        observation_count=3,
        confidence=0.5,
    )

    result = ProcessKpiPredictionResult(
        predictions=(prediction,),
    )

    with pytest.raises(AttributeError):
        result.predictions = ()


def test_prediction_result_count():
    prediction = KpiPrediction(
        kpi_name="Cycle Time",
        predicted_value=10.0,
        historical_average=10.0,
        observation_count=3,
        confidence=0.5,
    )

    result = ProcessKpiPredictionResult(
        predictions=(prediction,),
    )

    assert result.count == 1


def test_prediction_result_to_dict():
    prediction = KpiPrediction(
        kpi_name="Cycle Time",
        predicted_value=10.0,
        historical_average=10.0,
        observation_count=3,
        confidence=0.5,
    )

    result = ProcessKpiPredictionResult(
        predictions=(prediction,),
    )

    assert result.to_dict()["predictions"][0]["kpi_name"] == "Cycle Time"


# =============================================================================
# ProcessKpiPredictor
# =============================================================================


def test_predict_uses_historical_mean():
    predictor = ProcessKpiPredictor()

    result = predictor.predict(
        "Cycle Time",
        [10, 20, 30],
    )

    assert result.kpi_name == "Cycle Time"
    assert result.predicted_value == pytest.approx(20.0)
    assert result.historical_average == pytest.approx(20.0)
    assert result.observation_count == 3
    assert result.method == "historical_mean"


def test_predict_accepts_generators():
    predictor = ProcessKpiPredictor()

    values = (value for value in [10, 20, 30])

    result = predictor.predict(
        "Cycle Time",
        values,
    )

    assert result.predicted_value == pytest.approx(20.0)


def test_predict_single_observation():
    predictor = ProcessKpiPredictor()

    result = predictor.predict(
        "Cycle Time",
        [25],
    )

    assert result.predicted_value == pytest.approx(25.0)
    assert result.observation_count == 1
    assert result.confidence == pytest.approx(0.2)


def test_predict_stable_series_has_higher_confidence():
    predictor = ProcessKpiPredictor()

    stable = predictor.predict(
        "Cycle Time",
        [10, 10, 10, 10, 10],
    )

    variable = predictor.predict(
        "Cycle Time",
        [1, 5, 10, 20, 40],
    )

    assert stable.confidence > variable.confidence


def test_predict_more_observations_increases_confidence_for_stable_data():
    predictor = ProcessKpiPredictor()

    small = predictor.predict(
        "Cycle Time",
        [10, 10],
    )

    large = predictor.predict(
        "Cycle Time",
        [10, 10, 10, 10, 10, 10],
    )

    assert large.confidence > small.confidence


@pytest.mark.parametrize(
    "kpi_name",
    [
        "",
        "   ",
    ],
)
def test_predict_rejects_invalid_kpi_name(kpi_name):
    predictor = ProcessKpiPredictor()

    with pytest.raises(ProcessKpiPredictionError):
        predictor.predict(
            kpi_name,
            [10, 20, 30],
        )


@pytest.mark.parametrize(
    "values",
    [
        [],
        "123",
        [1, "invalid", 3],
        [True, 2, 3],
        None,
    ],
)
def test_predict_rejects_invalid_historical_values(values):
    predictor = ProcessKpiPredictor()

    with pytest.raises(ProcessKpiPredictionError):
        predictor.predict(
            "Cycle Time",
            values,
        )


def test_predict_many():
    predictor = ProcessKpiPredictor()

    result = predictor.predict_many(
        {
            "Cycle Time": [10, 20, 30],
            "Cost": [100, 200, 300],
        }
    )

    assert isinstance(result, ProcessKpiPredictionResult)
    assert result.count == 2

    assert result.predictions[0].kpi_name == "Cycle Time"
    assert result.predictions[0].predicted_value == pytest.approx(20.0)

    assert result.predictions[1].kpi_name == "Cost"
    assert result.predictions[1].predicted_value == pytest.approx(200.0)


def test_predict_many_is_deterministic():
    predictor = ProcessKpiPredictor()

    input_data = {
        "Cycle Time": [10, 20, 30],
        "Cost": [100, 200, 300],
    }

    first = predictor.predict_many(input_data)
    second = predictor.predict_many(input_data)

    assert first == second


def test_predict_many_rejects_invalid_input():
    predictor = ProcessKpiPredictor()

    with pytest.raises(ProcessKpiPredictionError):
        predictor.predict_many([])


# =============================================================================
# Convenience Functions
# =============================================================================


def test_predict_kpi_convenience_function():
    result = predict_kpi(
        "Cycle Time",
        [10, 20, 30],
    )

    assert result.predicted_value == pytest.approx(20.0)


def test_predict_kpis_convenience_function():
    result = predict_kpis(
        {
            "Cycle Time": [10, 20, 30],
            "Cost": [100, 200, 300],
        }
    )

    assert result.count == 2


def test_kpi_prediction_rejects_non_numeric_predicted_value() -> None:
    with pytest.raises(ProcessKpiPredictionError):
        KpiPrediction(
            kpi_name="Cycle Time",
            predicted_value="10.0",  # type: ignore[arg-type]
            historical_average=10.0,
            observation_count=3,
            confidence=0.5,
        )


def test_prediction_result_rejects_non_tuple_predictions() -> None:
    with pytest.raises(ProcessKpiPredictionError):
        ProcessKpiPredictionResult(
            predictions=[
                KpiPrediction(
                    kpi_name="Cycle Time",
                    predicted_value=10.0,
                    historical_average=10.0,
                    observation_count=3,
                    confidence=0.5,
                )
            ],  # type: ignore[arg-type]
        )