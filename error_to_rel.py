from helpers import _range_span

def convert_one_node(node, meas_value, meas_inst_range):
    """
    return: (rel_value, new_type)
    """
    if not isinstance(node, dict):
        return 0.0, "unknown"

    val = node.get("value", {}).get("real", 0.0)
    etype = (node.get("errorTypeId") or "").lower()

    match etype:
        case "relerr" | "относительная":
            return val, "relerr"

        case "abserr" | "абсолютная":
            if meas_value == 0:
                return 0.0, "relerr"
            return abs(val) / abs(meas_value), "relerr"

        case "fiderr" | "приведенная":
            # Извлекаем диапазон
            span = _range_span(meas_inst_range)
            if span <= 0 or meas_value == 0:
                return 0.0, "relerr"
            return val * (span / meas_value), "relerr"

        case _:
            return val, "unknown"



meas_inst_range = {
    "range": {"min": 0, "max": 5},  # Только промежуток
    "unit": "MPa"  # Передаём единицу измерения, но не извлекаем её
}

# Пример для погрешности
node = {
    "errorTypeId": "AbsErr",  # Абсолютная погрешность
    "value": {"real": 0.5}
}

measured_value = 10

# Вызов функции для преобразования погрешности
rel_value, new_type = convert_one_node(node, measured_value, meas_inst_range)

print(f"Относительная погрешность: {rel_value}")
print(f"Тип погрешности после преобразования: {new_type}")