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
        node = self.phys_props.get(self.pressure_key)
        if not node:
            return 0.0
        return convert_pressure(node, to_unit="pa")

    def compute(self):
        p_Pa = self._extract_measured_Pa()
        normalized_state = normalize_abs_errors_to_pa(self.err_state)   #костыльный нормализатор надо переписать и каждое поле тут обсосать
        effective_range = self.get_range_node(normalized_state)

        if effective_range:
            unit = effective_range["unit"].lower()
            r = effective_range["range"]
            min_raw = r.get("min", 0)
            max_raw = r.get("max", 0)

            range_min_Pa = convert_pressure({"real": min_raw, "unit": unit}, "pa")
            range_max_Pa = convert_pressure({"real": max_raw, "unit": unit}, "pa")

            self.check_range(
                p_Pa,
                range_min_Pa,
                range_max_Pa,
                name="Давление",
                unit_normalized="Pa",
                required=True
            )

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