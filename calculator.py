#!/usr/bin/env python3

import sys
import math
import re
from typing import Optional, List, Tuple
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QLineEdit, QLabel, QListWidget,
    QComboBox, QTabWidget, QMessageBox, QTextEdit, QRadioButton,
    QButtonGroup, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class NumberBaseConverter:
    ROMAN_MAP = [
        (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
        (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
        (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
    ]

    @staticmethod
    def validate_input(text: str, base: int) -> bool:
        if not text:
            return False
        if base == 10:
            try:
                float(text)
                return True
            except ValueError:
                return False
        elif base in [2, 8, 16]:
            try:
                int(text, base)
                return True
            except ValueError:
                return False
        return False

    @staticmethod
    def to_decimal(value: str, from_base: int) -> Optional[float]:
        try:
            if from_base == 10:
                return float(value)
            elif from_base in [2, 8, 16]:
                return float(int(value, from_base))
            elif from_base == -1:
                return float(NumberBaseConverter.roman_to_int(value))
            else:
                return float(int(value, from_base))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def from_decimal(value: float, to_base: int) -> Optional[str]:
        try:
            int_value = int(value)
            if to_base == 10:
                return str(value)
            elif to_base == 2:
                return bin(int_value)[2:]
            elif to_base == 8:
                return oct(int_value)[2:]
            elif to_base == 16:
                return hex(int_value)[2:].upper()
            elif to_base == -1:
                return NumberBaseConverter.int_to_roman(int_value)
            else:
                return NumberBaseConverter.to_custom_base(int_value, to_base)
        except (ValueError, TypeError, OverflowError):
            return None

    @staticmethod
    def int_to_roman(num: int) -> str:
        if num <= 0 or num >= 4000:
            raise ValueError("Římské číslice podporují pouze rozsah 1-3999")

        result = []
        for value, numeral in NumberBaseConverter.ROMAN_MAP:
            count = num // value
            if count:
                result.append(numeral * count)
                num -= value * count
        return ''.join(result)

    @staticmethod
    def roman_to_int(roman: str) -> int:
        roman = roman.upper()
        roman_values = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}

        total = 0
        prev_value = 0

        for char in reversed(roman):
            if char not in roman_values:
                raise ValueError(f"Neplatná římská číslice: {char}")
            value = roman_values[char]
            if value < prev_value:
                total -= value
            else:
                total += value
            prev_value = value

        return total

    @staticmethod
    def to_custom_base(num: int, base: int) -> str:
        if base < 2 or base > 36:
            raise ValueError("Soustava musí být mezi 2 a 36")

        if num == 0:
            return "0"

        digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = []
        negative = num < 0
        num = abs(num)

        while num > 0:
            result.append(digits[num % base])
            num //= base

        if negative:
            result.append('-')

        return ''.join(reversed(result))


class ExpressionEvaluator:
    ALLOWED_OPERATORS = {'+', '-', '*', '/', '(', ')', '.', '%'}
    ALLOWED_FUNCTIONS = {
        'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
        'log', 'ln', 'exp', 'sqrt', 'abs', 'pow'
    }

    @staticmethod
    def sanitize_expression(expr: str) -> str:
        expr = expr.strip()

        parts = re.split(r'[\+\-\*/\(\)]', expr)
        for part in parts:
            if part.count('.') > 1:
                raise ValueError("Více desetinných teček v čísle")

        return expr

    @staticmethod
    def evaluate(expr: str, angle_mode: str = 'deg') -> Optional[float]:
        try:
            expr = ExpressionEvaluator.sanitize_expression(expr)

            if re.search(r'/\s*0(?:\.\0*)?(?:[^\d]|$)', expr):
                raise ZeroDivisionError("Dělení nulou")

            expr = expr.replace('^', '**')

            if angle_mode == 'deg':
                expr = re.sub(r'sin\((.*?)\)', r'sin(radians(\1))', expr)
                expr = re.sub(r'cos\((.*?)\)', r'cos(radians(\1))', expr)
                expr = re.sub(r'tan\((.*?)\)', r'tan(radians(\1))', expr)

            safe_dict = {
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
                'log': math.log10, 'ln': math.log, 'exp': math.exp,
                'sqrt': math.sqrt, 'abs': abs, 'pow': pow,
                'radians': math.radians, 'degrees': math.degrees,
                'pi': math.pi, 'e': math.e,
                '__builtins__': {}
            }

            result = eval(expr, safe_dict, {})

            if math.isnan(result) or math.isinf(result):
                raise ValueError("Neplatný výsledek")

            return float(result)

        except ZeroDivisionError:
            raise ZeroDivisionError("Nelze dělit nulou")
        except SyntaxError:
            raise SyntaxError("Neplatná syntaxe výrazu")
        except (ValueError, TypeError, NameError) as e:
            raise ValueError(f"Neplatný výraz: {str(e)}")
        except Exception as e:
            raise Exception(f"Chyba vyhodnocení: {str(e)}")


class HistoryManager:
    def __init__(self):
        self.history: List[Tuple[str, str]] = []

    def add_entry(self, expression: str, result: str):
        self.history.append((expression, result))

    def get_history(self) -> List[str]:
        return [f"{expr} = {result}" for expr, result in self.history]

    def clear(self):
        self.history.clear()


class CalculatorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kalkulačka")
        self.setMinimumSize(500, 700)

        self.history_manager = HistoryManager()
        self.angle_mode = 'deg'

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.basic_tab = self.create_basic_calculator_tab()
        self.tabs.addTab(self.basic_tab, "Kalkulačka")

        self.base_tab = self.create_base_converter_tab()
        self.tabs.addTab(self.base_tab, "Převodník soustav")

        self.history_tab = self.create_history_tab()
        self.tabs.addTab(self.history_tab, "Historie")

    def create_basic_calculator_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(False)
        self.display.setFont(QFont("Arial", 18))
        self.display.setMinimumHeight(50)
        self.display.returnPressed.connect(self.calculate)
        layout.addWidget(self.display)

        angle_layout = QHBoxLayout()
        self.angle_group = QButtonGroup()
        self.deg_radio = QRadioButton("Stupně")
        self.rad_radio = QRadioButton("Radiány")
        self.deg_radio.setChecked(True)

        self.angle_group.addButton(self.deg_radio)
        self.angle_group.addButton(self.rad_radio)

        self.deg_radio.toggled.connect(lambda: self.set_angle_mode('deg'))
        self.rad_radio.toggled.connect(lambda: self.set_angle_mode('rad'))

        angle_layout.addWidget(self.deg_radio)
        angle_layout.addWidget(self.rad_radio)
        angle_layout.addStretch()
        layout.addLayout(angle_layout)

        # Button grid
        button_layout = QGridLayout()

        # Number buttons
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('/', 0, 3), ('C', 0, 4),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('*', 1, 3), ('(', 1, 4),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('-', 2, 3), (')', 2, 4),
            ('0', 3, 0), ('.', 3, 1), ('=', 3, 2), ('+', 3, 3), ('%', 3, 4),
        ]

        for text, row, col in buttons:
            button = QPushButton(text)
            button.setMinimumSize(60, 50)
            button.setFont(QFont("Arial", 14))
            if text == '=':
                button.clicked.connect(self.calculate)
            elif text == 'C':
                button.clicked.connect(self.clear_display)
            else:
                button.clicked.connect(lambda checked, t=text: self.add_to_display(t))
            button_layout.addWidget(button, row, col)

        layout.addLayout(button_layout)

        # Advanced functions
        func_layout = QGridLayout()
        functions = [
            ('sin', 0, 0), ('cos', 0, 1), ('tan', 0, 2),
            ('log', 1, 0), ('ln', 1, 1), ('exp', 1, 2),
            ('sqrt', 2, 0), ('x²', 2, 1), ('π', 2, 2),
        ]

        for text, row, col in functions:
            button = QPushButton(text)
            button.setMinimumSize(60, 40)
            if text == 'x²':
                button.clicked.connect(lambda: self.add_function('**2'))
            elif text == 'π':
                button.clicked.connect(lambda: self.add_to_display(str(math.pi)))
            else:
                button.clicked.connect(lambda checked, t=text: self.add_function(t))
            func_layout.addWidget(button, row, col)

        layout.addLayout(func_layout)

        return tab

    def create_base_converter_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Input section
        input_group = QGroupBox("Vstup")
        input_layout = QVBoxLayout(input_group)

        self.base_input = QLineEdit()
        self.base_input.setFont(QFont("Arial", 12))
        self.base_input.setPlaceholderText("Zadejte číslo...")
        input_layout.addWidget(self.base_input)

        self.from_base_combo = QComboBox()
        self.from_base_combo.addItems([
            "Desítková (10)", "Dvojková (2)", "Osmičková (8)",
            "Šestnáctková (16)", "Římská", "Vlastní"
        ])
        input_layout.addWidget(self.from_base_combo)

        self.custom_from_base = QLineEdit()
        self.custom_from_base.setPlaceholderText("Zadejte soustavu (2-36)")
        self.custom_from_base.hide()
        input_layout.addWidget(self.custom_from_base)

        self.from_base_combo.currentTextChanged.connect(self.toggle_custom_base_input)

        layout.addWidget(input_group)

        # Output section
        output_group = QGroupBox("Výstup")
        output_layout = QVBoxLayout(output_group)

        self.to_base_combo = QComboBox()
        self.to_base_combo.addItems([
            "Desítková (10)", "Dvojková (2)", "Osmičková (8)",
            "Šestnáctková (16)", "Římská", "Vlastní"
        ])
        output_layout.addWidget(self.to_base_combo)

        self.custom_to_base = QLineEdit()
        self.custom_to_base.setPlaceholderText("Zadejte soustavu (2-36)")
        self.custom_to_base.hide()
        output_layout.addWidget(self.custom_to_base)

        self.base_output = QLineEdit()
        self.base_output.setReadOnly(True)
        self.base_output.setFont(QFont("Arial", 12))
        self.base_output.setPlaceholderText("Výsledek...")
        output_layout.addWidget(self.base_output)

        self.to_base_combo.currentTextChanged.connect(self.toggle_custom_base_output)

        layout.addWidget(output_group)

        # Convert button
        convert_btn = QPushButton("Převést")
        convert_btn.setMinimumHeight(40)
        convert_btn.clicked.connect(self.convert_base)
        layout.addWidget(convert_btn)

        layout.addStretch()

        return tab

    def create_history_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.load_from_history)
        layout.addWidget(self.history_list)

        clear_btn = QPushButton("Vymazat historii")
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)

        return tab

    def add_to_display(self, text: str):
        current = self.display.text()
        self.display.setText(current + text)

    def add_function(self, func: str):
        current = self.display.text()
        if func == '**2':
            self.display.setText(f"({current})**2")
        else:
            self.display.setText(current + f"{func}(")

    def clear_display(self):
        self.display.clear()

    def set_angle_mode(self, mode: str):
        self.angle_mode = mode

    def calculate(self):
        expression = self.display.text()

        if not expression:
            return

        try:
            result = ExpressionEvaluator.evaluate(expression, self.angle_mode)
            result_str = str(result)

            # Add to history
            self.history_manager.add_entry(expression, result_str)
            self.update_history_display()

            # Display result
            self.display.setText(result_str)

        except ZeroDivisionError:
            self.show_error("Nelze dělit nulou!")
            self.display.clear()
        except Exception as e:
            self.show_error(f"Chyba: {str(e)}")
            self.display.clear()

    def convert_base(self):
        try:
            input_text = self.base_input.text()
            if not input_text:
                return

            # Get from base
            from_base_text = self.from_base_combo.currentText()
            if from_base_text == "Desítková (10)":
                from_base = 10
            elif from_base_text == "Dvojková (2)":
                from_base = 2
            elif from_base_text == "Osmičková (8)":
                from_base = 8
            elif from_base_text == "Šestnáctková (16)":
                from_base = 16
            elif from_base_text == "Římská":
                from_base = -1
            else:
                from_base = int(self.custom_from_base.text())
            to_base_text = self.to_base_combo.currentText()
            if to_base_text == "Desítková (10)":
                to_base = 10
            elif to_base_text == "Dvojková (2)":
                to_base = 2
            elif to_base_text == "Osmičková (8)":
                to_base = 8
            elif to_base_text == "Šestnáctková (16)":
                to_base = 16
            elif to_base_text == "Římská":
                to_base = -1
            else:
                to_base = int(self.custom_to_base.text())
            decimal_value = NumberBaseConverter.to_decimal(input_text, from_base)
            if decimal_value is None:
                raise ValueError("Neplatný vstup pro vybranou soustavu")

            result = NumberBaseConverter.from_decimal(decimal_value, to_base)
            if result is None:
                raise ValueError("Převod selhal")

            self.base_output.setText(result)

        except ValueError as e:
            self.show_error(f"Chyba převodu: {str(e)}")
            self.base_output.clear()
        except Exception as e:
            self.show_error(f"Chyba: {str(e)}")
            self.base_output.clear()

    def toggle_custom_base_input(self, text: str):
        if text == "Vlastní":
            self.custom_from_base.show()
        else:
            self.custom_from_base.hide()

    def toggle_custom_base_output(self, text: str):
        if text == "Vlastní":
            self.custom_to_base.show()
        else:
            self.custom_to_base.hide()

    def update_history_display(self):
        self.history_list.clear()
        self.history_list.addItems(self.history_manager.get_history())

    def load_from_history(self, item):
        text = item.text()
        if '=' in text:
            parts = text.split('=')
            expression = parts[0].strip()
            result = parts[1].strip()

            msg = QMessageBox()
            msg.setWindowTitle("Načíst z historie")
            msg.setText("Co chcete načíst?")
            expr_btn = msg.addButton("Výraz", QMessageBox.ActionRole)
            result_btn = msg.addButton("Výsledek", QMessageBox.ActionRole)
            msg.addButton("Zrušit", QMessageBox.RejectRole)

            msg.exec()

            if msg.clickedButton() == expr_btn:
                self.display.setText(expression)
            elif msg.clickedButton() == result_btn:
                self.display.setText(result)

            self.tabs.setCurrentIndex(0)

    def clear_history(self):
        self.history_manager.clear()
        self.update_history_display()

    def show_error(self, message: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Chyba")
        msg.setText(message)
        msg.exec()


def main():
    app = QApplication(sys.argv)

    app.setStyle('Fusion')

    calculator = CalculatorUI()
    calculator.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
