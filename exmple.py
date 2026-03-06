from validators import process_error_package


test1_error_state = {
    "complError": {
        "errorTypeId": "RelErr",
        "range": None,
        "value": {
            "real": 1.5,
            "unit": "percent"
        }
    },
    "intrError": None,
    "measInstRange": {
        "range": {
            "max": 10,
            "min": 0,
            "rangeType": "Inclusive"
        },
        "unit": "MPa"
    },
    "errorInputMethod": "ByValue",
    "uppError": None,
    "converterListProState": {
        "converters": []
    }
}

test2_error_state = {
    "complError": {
        "errorTypeId": "AbsErr",
        "range": None,
        "value": {
            "real": 0.15,
            "unit": "MPa"
        }
    },
    "intrError": None,
    "measInstRange": {
        "range": {
            "max": 6,
            "min": 0,
            "rangeType": "Inclusive"
        },
        "unit": "MPa"
    },
    "errorInputMethod": "ByValue",
    "uppError": None,
    "converterListProState": {
        "converters": []
    }
}

test3_error_state = {
    "complError": {
        "errorTypeId": "FidErr",
        "range": None,
        "value": {
            "real": 1.0,
            "unit": "percent"
        }
    },
    "intrError": {
        "errorTypeId": "FidErr",
        "range": None,
        "value": {
            "real": 0.5,
            "unit": "percent"
        }
    },
    "measInstRange": {
        "range": {
            "max": 3,
            "min": 0,
            "rangeType": "Inclusive"
        },
        "unit": "MPa"
    },
    "errorInputMethod": "ByValue",
    "uppError": None,
    "converterListProState": {
        "converters": []
    }
}


# Тест 1: RelErr
processed_error1 = process_error_package(test1_error_state, meas_value=5.0, target_type="rel")
print(f"Результат для теста 1 (RelErr): {processed_error1}")

# Тест 2: AbsErr
processed_error2 = process_error_package(test2_error_state, meas_value=5.0, target_type="rel")
print(f"Результат для теста 2 (AbsErr): {processed_error2}")

# Тест 3: FidErr
processed_error3 = process_error_package(test3_error_state, meas_value=2.5, target_type="rel")
print(f"Результат для теста 3 (FidErr): {processed_error3}")