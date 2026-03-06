from pressure.controller import PressureErrorController

# Пример 1: AbsErr
test1_error_state = {
    "complError": {
        "errorTypeId": "AbsErr",
        "range": None,
        "value": {
            "real": 3,
            "unit": "MPa"
        }
    },
    "constValue": None,
    "converterListProState": {
        "converters": []
    },
    "errorInputMethod": "ByValue",
    "intrError": {
        "errorTypeId": "AbsErr",
        "range": None,
        "value": {
            "real": 3,
            "unit": "MPa"
        }
    },
    "measInstRange": {
        "range": {
            "max": 6,
            "min": 0,
            "rangeType": "Inclusive"
        },
        "unit": "MPa"
    },
    "quantityValue": None,
    "slopeValue": None,
    "uppError": None
}

# Пример 2: FidErr
test2_error_state = {
    "complError": {
        "errorTypeId": "FidErr",
        "range": None,
        "value": {
            "real": 3,
            "unit": "percent"
        }
    },
    "constValue": None,
    "converterListProState": {
        "converters": []
    },
    "errorInputMethod": "ByValue",
    "intrError": {
        "errorTypeId": "FidErr",
        "range": None,
        "value": {
            "real": 3,
            "unit": "percent"
        }
    },
    "measInstRange": {
        "range": {
            "max": 6,
            "min": 0,
            "rangeType": "Inclusive"
        },
        "unit": "MPa"
    },
    "quantityValue": None,
    "slopeValue": None,
    "uppError": None
}

# Запуск теста
def test_pressure_controller():
    # Тест 1: AbsErr
    controller1 = PressureErrorController(
        phys_props={"p_abs": {"real": 5, "unit": "MPa"}},
        error_state=test1_error_state,
        pressure_key="p_abs"
    )
    result1 = controller1.compute()
    print(f"Результат для теста 1 (AbsErr): {result1}")

    # Тест 2: FidErr
    controller2 = PressureErrorController(
        phys_props={"p_abs": {"real": 3.0, "unit": "MPa"}},
        error_state=test2_error_state,
        pressure_key="p_abs"
    )
    result2 = controller2.compute()
    print(f"Результат для теста 2 (FidErr): {result2}")

# Запуск теста
test_pressure_controller()