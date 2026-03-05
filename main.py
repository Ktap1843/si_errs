class ErrorCalculator:
    def __init__(self, error_data):
        """
        Инициализация с данными в формате JSON.
        :param error_data: Словарь с данными погрешности.
        """
        self.error_data = error_data
        self.error_package = None

    def validate_data(self):
        validate_error_data(self.error_data)

    def process_error_package(self):
        """Обрабатывает и валидирует данные для расчета погрешностей."""
        self.validate_data()
        self.error_package = self.error_data.get("errorPackage", {})

    def compute_pressure_error(self):
        """Вычисляет погрешность давления."""
        if not self.error_package:
            raise ValueError("Error package is not processed.")

        pressure_controller = PressureErrorController(
            self.error_data.get("phys_props", {}),
            self.error_data.get("pressure_error_state", {}),
            "p_abs"  # Можно передать нужный ключ для давления
        )
        return pressure_controller.compute()

    def compute(self):
        """Выполняет расчет погрешностей для всех типов."""
        self.process_error_package()
        # Вычисление погрешности давления
        pressure_error_result = self.compute_pressure_error()
        # Можете добавить вызов других типов погрешностей и расчетов
        # например, для температуры, плотности и т.д.
        return pressure_error_result


if __name__ == "__main__":
    # Пример данных погрешностей
    error_data = {
        "phys_props": {
            "p_abs": {
                "real": 3,
                "unit": "MPa"
            }
        },
        "errorPackage": {
            "D20ErrorProState": {
                "complError": {"real": 0, "unit": "percent"},
                "intrError": {"real": 0, "unit": "percent"}
            }
        },
        "pressure_error_state": {
            "intrError": None,
            "complError": None,
            "converterListProState": {"converters": []},
            "measInstRange": None,
            "uppError": {
                "errorTypeId": "UppErr",
                "range": {
                    "range": {"min": 8.7, "max": 10, "rangeType": "Inclusive"},
                    "unit": "MPa"
                },
                "value": None
            }
        }
    }

    # Создание объекта для вычислений
    calculator = ErrorCalculator(error_data)
    result = calculator.compute()

    # Вывод результата
    print("Результаты вычислений погрешности давления:")
    print("p_Pa:", result["p_Pa"])
    print("range_Pa:", result["range_Pa"])
    print("u_base:", result["u_base"])
    print("u_conv:", result["u_conv"])
    print("u_total:", result["rel"])
    print("node:", result["node"])