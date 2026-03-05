# exmple.py
# Тестовый пример с ByFormula + AbsErr (твоя структура)

from validators import convert_pressure
from pressure.controller import PressureErrorController

# Измеренное значение (можно менять)
phys_props = {
    "p_abs": {
        "real": 3.0,          # текущее давление в MPa
        "unit": "MPa"
    }
}

PRESSURE_KEY = "p_abs"

# Твоя структура ошибки (ByFormula + AbsErr)
error_state = {
            "complError": {
                "errorTypeId": "AbsErr",
                "range": None,
                "value": {
                    "real": 3,
                    "unit": "Mpa"
                }
            },
            "constValue": 1,
            "converterListProState": {
                "converters": [
                ]
            },
            "errorInputMethod": "ByFormula",
            "intrError": None,
            "measInstRange": {
                "range": {
                    "max": 4,
                    "min": 0,
                    "rangeType": "Inclusive"
                },
                "unit": "MPa"
            },
            "quantityValue": "Pizm_Pmax",
            "slopeValue": 2,
            "uppError": None
        }

# Запуск расчёта
ctrl = PressureErrorController(
    phys_props=phys_props,
    error_state=error_state,
    pressure_key=PRESSURE_KEY
)

try:
    result = ctrl.compute()

    print("Результат расчёта (ByFormula + AbsErr):")
    print(f"  Измеренное давление: {result.get('p_Pa', 0)} Pa")
    print(f"  Диапазон: {result.get('range_Pa', 'нет')}")
    print(f"  Базовая погрешность (u_base): {result.get('u_base', 0)*100:.4f} %")
    print(f"  Итоговая относительная погрешность: {result.get('rel', 0)*100:.4f} %")
    print(f"  Стратегия: {result.get('strategy', 'не определено')}")
    print(f"  Узел ошибки (если есть): {result.get('node', 'нет')}")

except Exception as e:
    print("Ошибка при расчёте:")
    print(str(e))

