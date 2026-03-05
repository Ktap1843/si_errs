def _norm_unit(u):
    """Приводим единицу измерения к нижнему регистру и удаляем пробелы."""
    if not isinstance(u, str):
        return ""
    return u.strip().lower()

def _extract_value_and_unit(data):
    """Извлекаем значение и единицу из словаря."""
    if not isinstance(data, dict):
        return 0.0, ""

    val = data.get("value", data)
    if isinstance(val, dict):
        real = val.get("real", 0.0)
        unit = (val.get("unit") or "").lower()
    else:
        real = data.get("real", 0.0)
        unit = (data.get("unit") or "").lower()

    try:
        x = float(real)
    except Exception:
        x = 0.0

    return x, unit


def _range_span(range_node):
    """Вычисление диапазона (max - min)."""
    if isinstance(range_node, dict):
        r = range_node.get("range") or {}
        return float(r.get("max", 0)) - float(r.get("min", 0))
    return 0.0


def validate_positive(value, name="value"):
    if value <= 0:
        raise ValueError(f"{name} must be positive.")
    return value


def rss(*args, default=0.0):
    s2 = 0.0
    for a in args:
        v = float(a) if a is not None else default
        s2 += v * v
    return (s2)**0.5
