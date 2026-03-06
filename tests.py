import pytest
from pressure.controller import PressureErrorController

# Пример: Parametrize тестов
@pytest.mark.parametrize(
    "test_name, error_state, meas_value, expected_result",
    [
        (
            "1",
            {

                    "complError": {
                        "errorTypeId": "RelErr",
                        "range": None,
                        "value": {"real": 1.1, "unit": "percent"}
                    },
                    "constValue": 1,
                    "converterListProState": {"converters": []},
                    "errorInputMethod": "ByFormula",
                    "intrError": None,
                    "measInstRange": {
                        "range": {"max": 6, "min": 0, "rangeType": "Inclusive"},
                        "unit": "MPa"
                    },
                    "quantityValue": "Pmax_Pizm",
                    "slopeValue": 2,
                    "uppError": None

            },
            3.0,
            {'rel': 5.119570294468081}
        ),
        (
            "2",
            {

                    "complError": {
                        "errorTypeId": "AbsErr",
                        "range": None,
                        "value": {"real": 0.99, "unit": "MPa"}
                    },
                    "constValue": 0.5,
                    "converterListProState": {"converters": []},
                    "errorInputMethod": "ByFormula",
                    "intrError": None,
                    "measInstRange": {
                        "range": {"max": 6, "min": 0, "rangeType": "Inclusive"},
                        "unit": "MPa"
                    },
                    "quantityValue": "Pizm_Pmax",
                    "slopeValue": 0.7,
                    "uppError": None

            },
            3.0,
            {'rel': 43.494571819685476}
        ),
        (
            "3",
            {

                    "complError": {
                        "errorTypeId": "FidErr",
                        "range": None,
                        "value": {"real": 0.999, "unit": "percent"}
                    },
                    "constValue": 0.7,
                    "converterListProState": {"converters": []},
                    "errorInputMethod": "ByFormula",
                    "intrError": None,
                    "measInstRange": {
                        "range": {"max": 6, "min": 0, "rangeType": "Inclusive"},
                        "unit": "MPa"
                    },
                    "quantityValue": "Pizm_Pmax",
                    "slopeValue": 0.88,
                    "uppError": None

            },
            3.0,
            {'rel': 3.03156791116412}
        ),
        (
            "4",
            {

                    "complError": {
                        "errorTypeId": "AbsErr",
                        "range": None,
                        "value": {"real": 2, "unit": "MPa"}
                    },
                    "constValue": None,
                    "converterListProState": {"converters": []},
                    "errorInputMethod": "ByValue",
                    "intrError": {
                        "errorTypeId": "AbsErr",
                        "range": None,
                        "value": {"real": 1, "unit": "MPa"}
                    },
                    "measInstRange": {
                        "range": {"max": 6, "min": 0, "rangeType": "Inclusive"},
                        "unit": "MPa"
                    },
                    "quantityValue": None,
                    "slopeValue": None,
                    "uppError": None

            },
            3.0,
            {'rel': 74.535599249993}
        ),
        (
            "5",
            {

                    "complError": {
                        "errorTypeId": "AbsErr",
                        "range": None,
                        "value": {"real": 2, "unit": "MPa"}
                    },
                    "constValue": None,
                    "converterListProState": {"converters": []},
                    "errorInputMethod": "ByValue",
                    "intrError": {
                        "errorTypeId": "FidErr",
                        "range": None,
                        "value": {"real": 1, "unit": "percent"}
                    },
                    "measInstRange": {
                        "range": {"max": 6, "min": 0, "rangeType": "Inclusive"},
                        "unit": "MPa"
                    },
                    "quantityValue": None,
                    "slopeValue": None,
                    "uppError": None

            },
            3.0,
            {'rel': 4.47213595499958}
        ),
        (
            "6",
            {
                    "complError": {
                        "errorTypeId": "RelErr",
                        "range": None,
                        "value": {"real": 17, "unit": "percent"}
                    },
                    "constValue": None,
                    "converterListProState": {"converters": []},
                    "errorInputMethod": "ByValue",
                    "intrError": {
                        "errorTypeId": "RelErr",
                        "range": None,
                        "value": {"real": 1, "unit": "percent"}
                    },
                    "measInstRange": {
                        "range": {"max": 6, "min": 0, "rangeType": "Inclusive"},
                        "unit": "MPa"
                    },
                    "quantityValue": None,
                    "slopeValue": None,
                    "uppError": None
            },
            3.0,
            {'rel': 17.029386365926403}
        ),
        (
            "7",
            {
                    "complError": None,
                    "constValue": None,
                    "converterListProState": {"converters": []},
                    "errorInputMethod": None,
                    "intrError": None,
                    "measInstRange": None,
                    "quantityValue": None,
                    "slopeValue": None,
                    "uppError": {
                        "errorTypeId": "UppErr",
                        "range": {
                            "range": {"max": 6, "min": 0, "rangeType": "Inclusive"},
                            "unit": "MPa"
                        },
                        "value": None
                    }
            },
            3.0,
            {'rel': 100}
        )
    ]
)
def test_error_processing(test_name, error_state, meas_value, expected_result):
    controller = PressureErrorController(
        phys_props={"p_abs": {"real": meas_value, "unit": "MPa"}},
        error_state=error_state,
        pressure_key="p_abs"
    )
    result = controller.compute()

    assert result == expected_result, f"Test failed for {test_name}, got {result} instead"