from validators import make_rel_error_node, compute_upp_rel, process_error_package
from helpers import rss

#todo fiderr над ошибку найти некорректно переводит основную погрешность вроде

class BaseErrorController:
    """Базовый класс для всех контроллеров погрешностей"""
    def _handle_upp_error(self, error_state):
        upp = (error_state or {}).get("uppError")
        if upp:
            u_upp = compute_upp_rel(upp)
            return {
                "rel": u_upp,
                "node": make_rel_error_node(u_upp),
                "u_base": u_upp,
                "u_conv": 0.0,
                "conv_errors": [],
                "is_upp": True
            }
        return None

    def _process_base_error(self, error_state, meas_value=None, range_node=None):
        """Базовая погрешность"""
        if not error_state:
            error_state = {}

        upp = error_state.get("uppError")
        if upp:
            u_rel = compute_upp_rel(upp) / 100.0
            return {
                "u_base": u_rel,
                "node": make_rel_error_node(u_rel * 100),
                "strategy": "upp"}

        method = (error_state.get("errorInputMethod") or "ByValue").strip().lower()
        processed = process_error_package(
            error_state,
            meas_value=meas_value,
            target_type="rel")

        compl = processed.get("complError", {}).get("value", {}).get("real", 0.0)
        intr = processed.get("intrError", {}).get("value", {}).get("real", 0.0)

        u_base = rss(compl, intr)

        u_form = 0.0
        if method == "byformula":
            const_value = error_state.get("constValue")
            slope_value = error_state.get("slopeValue")
            quantity = (error_state.get("quantityValue") or "").lower()

            c = float(const_value) if const_value is not None else 0.0
            m = float(slope_value) if slope_value is not None else 0.0

            x_norm = 0.0
            if quantity in ("pizm_pmax", "qizm_qmax"):
                if range_node and meas_value is not None:
                    r_max = range_node.get("range", {}).get("max", 0.0)
                    if r_max != 0.0:
                        x_norm = abs(meas_value) / r_max
            elif quantity in ("pmax_pizm", "qmax_qizm"):
                if range_node and meas_value is not None and meas_value != 0.0:
                    r_max = range_node.get("range", {}).get("max", 0.0)
                    x_norm = r_max / abs(meas_value)

            delta = c + m * x_norm

            main_err_node = error_state.get("complError") or error_state.get("intrError") or {}
            err_type = main_err_node.get("errorTypeId", "RelErr").lower()


            fake_node = {
                "errorTypeId": err_type,
                "value": {"real": delta, "unit": "percent"},
                "range": range_node
            }

            fake_package = {"complError": fake_node}
            processed_fake = process_error_package(
                fake_package,
                meas_value=meas_value,
                target_type="rel"
            )

            u_form = processed_fake["complError"]["value"]["real"]

        u_total_base = rss(u_base, u_form)

        return {
            "u_base": u_total_base,
            "node": make_rel_error_node(u_total_base * 100),
            "strategy": method
        }

    def get_range_node(self, error_state):
        """
        Возвращает диапазон для расчёта погрешности.
        """
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

        meas_range = error_state.get("measInstRange")
        if meas_range:
            return {
                "range": meas_range.get("range", {}),
                "unit": meas_range.get("unit", "unknown"),
                "source": "measInstRange"
            }

        return None

    def check_range(self, measured_normalized, min_val, max_val, name="значение", unit_normalized="", required=False):
        """
            measured_normalized — измеренное значение (в базовых единицах СИ)
            min_val             — минимальное значение диапазона (в базовых единицах СИ)
            max_val             — максимальное значение диапазона (в базовых единицах СИ)
            name                — название для сообщения ошибки ("Давление", "Температура")
            unit_normalized     — единица для сообщения ошибки ("Pa", "K")
            required            — если True, то обязательно передавать, если False, то пропустит если диапазона нет
        """
        if min_val is None or max_val is None:
            if required:
                raise ValueError(f"Отсутствует min или max в диапазоне для {name}")
            return

        try:
            min_f = min_val
            max_f = max_val
        except (TypeError, ValueError):
            if required:
                raise ValueError(f"Некорректный формат min/max для {name}")
            return

        if max_f <= 0:
            if required:
                raise ValueError(f"Некорректный диапазон для {name}: max ≤ 0")
            return

        if min_f >= max_f:
            if required:
                raise ValueError(f"Некорректный диапазон для {name}: min ≥ max")
            return

        if not (min_f <= measured_normalized <= max_f):
            raise ValueError(
                f"{name.capitalize()} {measured_normalized} {unit_normalized} "
                f"не входит в диапазон {min_f} .. {max_f} {unit_normalized}")