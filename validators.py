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


from helpers import _range_span

def process_error_package(error_package, meas_value=None, target_type="rel"):
    if not isinstance(error_package, dict):
        return {"complError": 0.0, "intrError": 0.0}

    target = target_type.lower().strip()

    def convert_one_node(node):
        """Переводит одну погрешность в относительную"""
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
                return abs(val) * 100 / abs(meas_value), "relerr"

            case "fiderr" | "приведенная":
                span = _range_span(error_package.get("measInstRange", {}))
                if span <= 0 or meas_value == 0:
                    return 0.0, "relerr"
                return val * (span / meas_value), "relerr"

            case _:
                return val, "unknown"

    compl_node = error_package.get("complError", {})
    intr_node = error_package.get("intrError", {})

    compl_val, compl_new_type = convert_one_node(compl_node)
    intr_val, intr_new_type = convert_one_node(intr_node)

    return {
        "complError": {
            "errorTypeId": compl_new_type,
            "value": {"real": compl_val, "unit": "percent"}
        },
        "intrError": {
            "errorTypeId": intr_new_type,
            "value": {"real": intr_val, "unit": "percent"}
        }
    }
