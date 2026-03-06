from validators import convert_pressure

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

    def _extract_range(self, error_state):
        # Извлекаем диапазон из error_state и конвертируем в Паскали
        upp = error_state.get("uppError")
        if upp:
            upp_range = upp.get("range")
            if upp_range:
                return self._convert_range_to_si(upp_range)

        meas_range = error_state.get("measInstRange")
        if meas_range:
            return self._convert_range_to_si(meas_range["range"])

        return None

    def _convert_range_to_si(self, range_data):
        """Конвертируем диапазон в Паскали"""
        min_value = range_data.get("min", 0)
        max_value = range_data.get("max", 0)
        unit = range_data.get("unit", "MPa")

        min_Pa = convert_pressure({"real": min_value, "unit": unit}, "pa")
        max_Pa = convert_pressure({"real": max_value, "unit": unit}, "pa")

        return min_Pa, max_Pa

    def check_range(self, measured_normalized, min_val, max_val, name="значение", unit_normalized="", required=False):
        """
        Проверка, что измеренное значение находится в допустимом диапазоне
        :param measured_normalized: измеренное значение (в базовых единицах)
        :param min_val: минимальное значение диапазона (в базовых единицах)
        :param max_val: максимальное значение диапазона (в базовых единицах)
        :param name: название значения для ошибки (например, "Давление")
        :param unit_normalized: единица измерения
        :param required: если True, проверка обязательна, если False, диапазон может быть опциональным
        """
        if min_val is None or max_val is None:
            if required:
                raise ValueError(f"Отсутствует min или max в диапазоне для {name}")
            return

        if max_val <= 0:
            if required:
                raise ValueError(f"Некорректный диапазон для {name}: max ≤ 0")
            return

        if min_val >= max_val:
            if required:
                raise ValueError(f"Некорректный диапазон для {name}: min ≥ max")
            return

        if not (min_val <= measured_normalized <= max_val):
            raise ValueError(
                f"{name.capitalize()} {measured_normalized} {unit_normalized} "
                f"не входит в диапазон {min_val} .. {max_val} {unit_normalized}")

    def compute_by_formula(self, error_state, range_node=None, meas_value=None):
        """
        Вычисление delta по формуле, учитывая constValue, slopeValue и quantityValue.
        :param error_state: Состояние ошибки.
        :param range_node: Диапазон значений (если необходимо для вычислений).
        :param meas_value: Измеренное значение (если используется в расчетах).
        :return: delta - вычисленное значение.
        """
        const_value = error_state.get("constValue", 0.0)
        slope_value = error_state.get("slopeValue", 0.0)
        quantity_value = (error_state.get("quantityValue") or "").lower()

        c = float(const_value) if const_value is not None else 0.0
        m = float(slope_value) if slope_value is not None else 0.0
        x_norm = 0.0

        # Расчет нормализованного значения для формулы
        if quantity_value in ("pizm_pmax", "qizm_qmax"):
            if range_node and meas_value is not None:
                r_max = range_node.get("range", {}).get("max", 0.0)
                if r_max != 0.0:
                    x_norm = abs(meas_value) / r_max
        elif quantity_value in ("pmax_pizm", "qmax_qizm"):
            if range_node and meas_value is not None and meas_value != 0.0:
                r_max = range_node.get("range", {}).get("max", 0.0)
                x_norm = r_max / abs(meas_value)

        # Вычисление delta
        delta = c + m * x_norm

        return delta

    def process_error_package(self, error_package, meas_value=None, target_type="rel", range_node=None):
        """Обработка погрешностей"""
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

        if error_package.get("errorInputMethod") == "ByFormula":
            delta = self.compute_by_formula(error_package, range_node=range_node, meas_value=meas_value)

            intr_error_node = {
                "errorTypeId": compl_node.get("errorTypeId", "unknown"),
                "value": {"real": delta, "unit": compl_node.get("value", {}).get("unit", "percent")}
            }
            error_package["intrError"] = intr_error_node

        compl_val, compl_new_type = convert_one_node(compl_node)
        intr_node = error_package.get("intrError", {})
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