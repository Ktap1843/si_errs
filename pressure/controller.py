from validators import convert_pressure
from common.base_controller import BaseErrorController
from helpers import rss
from pressure.normalizers import normalize_abs_errors_to_pa

class PressureErrorController(BaseErrorController):
    def __init__(self, phys_props: dict, error_state: dict, pressure_key: str = "p_abs"):
        self.phys_props = phys_props or {}
        self.err_state = error_state or {}
        self.pressure_key = pressure_key

    def _extract_measured_Pa(self):
        """Извлекает давление и конвертирует в Паскали"""
        node = self.phys_props.get(self.pressure_key)
        if not node:
            return 0.0
        return convert_pressure(node, to_unit="pa")

    def convert_range_to_si(self, range_data):
        """
        Конвертирует диапазон в Паскали.
        :param range_data: словарь с полями 'min', 'max' и 'unit'.
        :return: min_Pa, max_Pa - конвертированные значения диапазона в Паскали
        """
        if not isinstance(range_data, dict):
            raise ValueError("Диапазон должен быть словарем.")

        min_value = range_data.get("min", 0)
        max_value = range_data.get("max", 0)
        unit = range_data.get("unit", "MPa")  # По умолчанию предполагаем, что единица - MPa.

        # Преобразуем диапазон в Паскали
        min_Pa = convert_pressure({"real": min_value, "unit": unit}, "pa")
        max_Pa = convert_pressure({"real": max_value, "unit": unit}, "pa")

        return min_Pa, max_Pa

    def get_range_node(self, error_state):
        """
        Возвращает диапазон для расчёта погрешности.
        Извлекает диапазон из `measInstRange` или `uppError`.
        """
        # Проверяем в `uppError`
        upp = error_state.get("uppError")
        if upp:
            upp_range = upp.get("range")
            if upp_range:
                return {
                    "range": upp_range.get("range", {}),
                    "unit": upp_range.get("unit", "unknown"),
                    "source": "uppError"
                }
            return None

        # Если в `uppError` нет диапазона, проверяем в `measInstRange`
        meas_range = error_state.get("measInstRange")
        if meas_range:
            return {
                "range": meas_range.get("range", {}),
                "unit": meas_range.get("unit", "unknown"),
                "source": "measInstRange"
            }

        return None  # Если диапазона нет, возвращаем None

    def compute(self):
        p_Pa = self._extract_measured_Pa()
        effective_range = self.get_range_node(self.err_state)

        if effective_range:
            range_min = effective_range["range"]["min"]
            range_max = effective_range["range"]["max"]
            unit = effective_range["unit"]
            range_min_Pa = convert_pressure({"real": range_min, "unit": unit}, "pa")
            range_max_Pa = convert_pressure({"real": range_max, "unit": unit}, "pa")
            self.check_range(p_Pa, range_min_Pa, range_max_Pa, name="Давление", unit_normalized="Pa", required=True)
            range_node_pa = {
                "range": {
                    "min": range_min_Pa,
                    "max": range_max_Pa,
                    "rangeType": "Inclusive"
                },
                "unit": "Pa"
            }

            range_Pa = {"min": range_min_Pa, "max": range_max_Pa, "unit": "Pa"}
        else:
            raise ValueError("Отсутствует диапазон для давления")

        normalized_state = normalize_abs_errors_to_pa(self.err_state)
        normalized_state["measInstRange"]["range"]["max"] = range_max_Pa
        normalized_state["measInstRange"]["range"]["min"] = range_min_Pa
        normalized_state["measInstRange"]["unit"] = "Pa"

        upp_result = self._handle_upp_error(normalized_state)
        if upp_result:
            upp_result["p_Pa"] = p_Pa
            return upp_result

        base = self._process_base_error(
            normalized_state,
            meas_value=p_Pa,
            range_node=range_node_pa
        )

        u_conv = 0.0
        conv_errors = []

        u_total = rss(base["u_base"], u_conv)

        return {
            "rel": u_total,
            "p_Pa": p_Pa,
            "range_Pa": range_Pa,
            "u_base": base["u_base"],
            "u_conv": u_conv,
            "conv_errors": conv_errors,
        }