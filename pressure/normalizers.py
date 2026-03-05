from validators import convert_pressure


def normalize_abs_errors_to_pa(error_state):
    if not error_state or not isinstance(error_state, dict):
        return error_state

    normalized = error_state.copy()

    # Функция для нормализации значений в Паскали
    def normalize_value(val, unit):
        if val is None or unit is None:
            return val
        try:
            return convert_pressure({"real": val, "unit": unit}, "pa")
        except:
            return val

    main_node = normalized.get("complError", {})
    main_type = main_node.get("errorTypeId", "").lower()
    is_rel_main = "rel" in main_type or "fid" in main_type or "percent" in main_type.lower()

    # Рекурсивная функция для нормализации всех узлов в структуре
    def normalize_node(node, is_rel_main):
        if not node or not isinstance(node, dict):
            return node

        new_node = node.copy()

        # Обработка значений с unit
        value = new_node.get("value")
        if value and isinstance(value, dict):
            real = value.get("real")
            unit = value.get("unit")

            if real is not None and unit and unit.lower() != "percent":
                real_pa = normalize_value(real, unit)
                new_value = value.copy()
                new_value["real"] = real_pa
                new_value["unit"] = "Pa"
                new_node["value"] = new_value

        # Рекурсия для вложенных узлов
        for key, val in new_node.items():
            if isinstance(val, dict):
                new_node[key] = normalize_node(val, is_rel_main)
            elif isinstance(val, list):
                new_node[key] = [normalize_node(item, is_rel_main) if isinstance(item, dict) else item for item in val]

        return new_node

    normalized = normalize_node(normalized, is_rel_main)

    if "constValue" in normalized and normalized["constValue"] is not None:
        const_value = normalized["constValue"]
        if isinstance(const_value, dict):
            unit = const_value.get("unit")
            if unit and unit.lower() != "percent":
                normalized["constValue"] = normalize_value(const_value["real"], unit)
        else:
            if not is_rel_main:
                normalized["constValue"] = normalize_value(const_value, "MPa")

    if "slopeValue" in normalized and normalized["slopeValue"] is not None:
        slope_value = normalized["slopeValue"]
        if isinstance(slope_value, dict):
            unit = slope_value.get("unit")
            if unit and unit.lower() != "percent":
                normalized["slopeValue"] = normalize_value(slope_value["real"], unit)
        else:
            if not is_rel_main:
                normalized["slopeValue"] = normalize_value(slope_value, "MPa")

    return normalized