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

test2_error_state = {
    "complError": {
        "errorTypeId": "AbsErr",
        "range": None,
        "value": {
            "real": 1,
            "unit": "MPa"
        }
    },
    "constValue": 1,
    "converterListProState": {
        "converters": []
    },
    "errorInputMethod": "ByFormula",
    "intrError": None,
    "measInstRange": {
        "range": {
            "max": 6,
            "min": 0,
            "rangeType": "Inclusive"
        },
        "unit": "MPa"
    },
    "quantityValue": "Pizm_Pmax",
    "slopeValue": 2,
    "uppError": None
}

# Тест с использованием `uppError`
test3_error_state = {
    'complError': {
        'errorTypeId': 'AbsErr',
        'range': None,
        'value': {'real': 3, 'unit': 'MPa'}
    },
    'constValue': None,
    'converterListProState': {'converters': []},
    'errorInputMethod': 'ByValue',
    'intrError': {
        'errorTypeId': 'AbsErr',
        'range': None,
        'value': {'real': 0.5, 'unit': 'MPa'}
    },
    'measInstRange': {
        'range': {
            'max': 6000000.0,
            'min': 0.0,
            'rangeType': 'Inclusive'
        },
        'unit': 'Pa'
    },
    'quantityValue': None,
    'slopeValue': None,
    'uppError': {
        'errorTypeId': 'UppErr',
        'range': {
            'range': {
                'max': 6,
                'min': 0,
                'rangeType': 'Inclusive'
            },
            'unit': 'MPa'
        },
        'value': None
    }
}

# Запуск теста
def test_pressure_controller():
    # #Тест 1: AbsErr
    # controller1 = PressureErrorController(
    #     phys_props={"p_abs": {"real": 5, "unit": "MPa"}},
    #     error_state=test1_error_state,
    #     pressure_key="p_abs"
    # )
    # result1 = controller1.compute()
    # print(f"Результат для теста 1 (AbsErr): {result1}")

    # Тест 2: FidErr
    controller2 = PressureErrorController(
        phys_props={"p_abs": {"real": 3.0, "unit": "MPa"}},
        error_state=test2_error_state,
        pressure_key="p_abs"
    )
    result2 = controller2.compute()
    print(f"Результат для теста 2 (FidErr): {result2}")

    # # Тест 3: UppErr
    # controller3 = PressureErrorController(
    #     phys_props={"p_abs": {"real": 5, "unit": "MPa"}},
    #     error_state=test3_error_state,
    #     pressure_key="p_abs"
    # )
    # result3 = controller3.compute()
    # print(f"Результат для теста 3 (UppErr): {result3}")
    #

# Запуск теста
test_pressure_controller()
