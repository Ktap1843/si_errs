from helpers import _range_span
from validators import process_error_package, make_rel_error_node, compute_upp_rel

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
                "strategy": "upp"
            }

        method = (error_state.get("errorInputMethod") or "ByValue").strip().lower()
        processed = process_error_package(
            error_state,
            meas_value=meas_value,
            target_type="rel"
        )

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

            fake_node = {
                "errorTypeId": "RelErr",
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