from helpers import (
    _norm_unit,
    _extract_value_and_unit,
    validate_positive,
    _range_span,
)

_P_TO_PA = {
    "pa": 1.0,
    "pascal": 1.0,
    "pascals": 1.0,
    "kpa": 1000.0,
    "mpa": 1000000.0,
    "bar": 100000.0,
    "bars": 100000.0,
    "atm": 101325.0,
    "torr": 133.32,
    "mmhg": 133.32,
    "mm_hg": 133.32,
    "mmh2o": 9.80665,
    "kgf_cm2": 98066.5,
    "kgf/m2": 9.80665,
}

_RHO_TO_KGM3 = {
    "kg_m3": 1.0,
    "kg/m3": 1.0,
    "kgm3": 1.0,
    "g_cm3": 1000.0,
    "g/cm3": 1000.0,
    "gcm3": 1000.0,
}

def convert_pressure(data, to_unit="pa"):
    value, from_unit = _extract_value_and_unit(data)
    fu = _norm_unit(from_unit)
    tu = _norm_unit(to_unit)

    if fu not in _P_TO_PA:
        raise ValueError(f"Неизвестная единица давления: '{from_unit}'")
    if tu not in _P_TO_PA:
        raise ValueError(f"Неизвестная целевая единица давления: '{to_unit}'")

    pa = value * _P_TO_PA[fu]
    return pa / _P_TO_PA[tu]


def convert_density(data, to_unit="kg_m3"):
    value, from_unit = _extract_value_and_unit(data)
    fu = _norm_unit(from_unit)
    tu = _norm_unit(to_unit)

    if fu not in _RHO_TO_KGM3:
        raise ValueError(f"Неизвестная единица плотности: '{from_unit}'")
    if tu not in _RHO_TO_KGM3:
        raise ValueError(f"Неизвестная целевая единица плотности: '{to_unit}'")

    base = value * _RHO_TO_KGM3[fu]
    return base / _RHO_TO_KGM3[tu]


def convert_temperature(data, to_unit="k"):
    value, from_unit = _extract_value_and_unit(data)
    fu = _norm_unit(from_unit)

    if fu in ("c", "degc", "°c", "celsius", "с"):
        v_k = value + 273.15
    elif fu in ("k", "kelvin"):
        v_k = value
    else:
        raise ValueError(f"Неизвестная единица температуры: '{from_unit}' (поддерживается: °C, K)")

    tu = _norm_unit(to_unit)
    if tu in ("k", "kelvin"):
        if v_k < 0:
            raise ValueError(
                f"Температура не может быть отрицательной в Кельвинах: {v_k:.3f} K "
                f"(исходное значение: {value} {from_unit})")
        return v_k

    elif tu in ("c", "degc", "°c", "celsius"):
        return v_k - 273.15

    else:
        raise ValueError(f"Неизвестная целевая единица температуры: '{to_unit}' (поддерживается: °C, K)")


def make_rel_error_node(rel_value: float):
    """Создаёт узел RelErr в формате percent"""
    return {
        "errorTypeId": "RelErr",
        "range": None,
        "value": {
            "real": float(rel_value),
            "unit": "percent"
        }
    }


def compute_upp_rel(upp_node):
    """UppErr"""
    if not isinstance(upp_node, dict):
        return 0.0
    rng = upp_node.get("range") or {}
    r = rng.get("range") or rng

    y_min = (r.get("min", 0))
    y_max = (r.get("max", 0))

    if y_min >= y_max or y_max == 0:
        raise ValueError(f"Некорректный диапазон, min={y_min} >= max={y_max} или max=0")

    d = y_max + y_min
    return abs((y_max - y_min) * 100 / d)


def process_error_package(error_package, meas_value=None, target_type="rel"):
    if not isinstance(error_package, dict):
        return {"complError": 0.0, "intrError": 0.0}

    target = target_type.lower().strip()

    def convert_one_node(node):
        """
        Переводит одну погрешность (complError или intrError) в относительную.
        Возвращает: (rel_value, new_type, original_unit)
        """
        if not isinstance(node, dict):
            return 0.0, "unknown", ""

        # Достаём значение и единицу
        val, unit = _extract_value_and_unit(node.get("value", {}))
        etype = (node.get("errorTypeId") or "").lower()

        unit_norm = unit.lower().replace(" ", "").replace("%", "percent")
        is_percent = "percent" in unit_norm


        # RelErr — уже относительная
        if "relerr" in etype or "отн" in etype:
            current_rel = val if is_percent else val

        # AbsErr — абсолютная → переводим в относительную
        elif "abserr" in etype or "абс" in etype:
            if meas_value is None or meas_value == 0:
                current_rel = 0.0
            else:
                current_rel = abs(val) *100 / abs(meas_value)

        # FidErr / приведённая
        elif "fiderr" in etype or "прив" in etype or "gamma" in etype or "γ" in etype:
            span = _range_span(error_package.get("measInstRange", {}))
            if span <= 0 or meas_value is None or meas_value == 0:
                current_rel = 0.0
            else:
                gamma = val if is_percent else val
                current_rel = gamma * (span / meas_value)

        # UppErr — fallback (если вдруг попадётся)
        elif "upp" in etype:
            upp_max = error_package.get("measInstRange", {}).get("range", {}).get("max", 0)
            if upp_max <= 0:
                current_rel = 0.0
            else:
                current_rel = val / 100.0 if is_percent else val / upp_max

        # Неизвестный тип, но есть %
        else:
            current_rel = val if is_percent else val

        original_unit = unit if unit else "unknown"

        if target in ("rel", "relative", "отн"):
            return current_rel, "RelErr", original_unit

        elif target in ("rel%", "percent", "процент", "%"):
            return current_rel, "RelErr (%)", original_unit

        elif target in ("abs", "absolute", "абс"):
            if meas_value is None:
                return 0.0, "AbsErr", original_unit
            return current_rel, "AbsErr", original_unit

        elif target in ("fid", "reduced", "приведённая", "gamma", "γ"):
            span = _range_span(error_package.get("measInstRange", {}))
            if span <= 0:
                return 0.0, "FidErr", original_unit
            fid_value = current_rel * (meas_value / span) if meas_value != 0 else 0.0
            return fid_value, "FidErr (%)", original_unit

        else:
            return current_rel, "unknown", original_unit

    compl_node = error_package.get("complError", {})
    intr_node = error_package.get("intrError", {})

    compl_val, compl_new_type, compl_unit = convert_one_node(compl_node)
    intr_val, intr_new_type, intr_unit = convert_one_node(intr_node)

    return {
        "complError": {
            "errorTypeId": compl_new_type,
            "value": {"real": compl_val, "unit": compl_unit}
        },
        "intrError": {
            "errorTypeId": intr_new_type,
            "value": {"real": intr_val, "unit": intr_unit}
        },
        "measInstRange": error_package.get("measInstRange"),
        "uppError": error_package.get("uppError"),
    }
