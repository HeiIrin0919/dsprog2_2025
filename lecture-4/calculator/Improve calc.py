import flet as ft
import math


class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text


class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = "#1a1a2e"
        self.color = "#ffffff"
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            shadow_color="#00fff5",
            elevation=5,
        )


class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = "#ff2e63"
        self.color = "#ffffff"
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            shadow_color="#ff2e63",
            elevation=8,
        )


class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = "#252541"
        self.color = "#00fff5"
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            shadow_color="#00fff5",
            elevation=5,
        )


class ScientificButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = "#0f0f23"
        self.color = "#08f7fe"
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            shadow_color="#08f7fe",
            elevation=6,
        )


class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.expression = ""
        
        self.formula_display = ft.Text(
            value="", 
            color="#08f7fe", 
            size=16,
            text_align=ft.TextAlign.RIGHT,
            font_family="Consolas",
        )
        
        self.result = ft.Text(
            value="0", 
            color="#ffffff", 
            size=36,
            text_align=ft.TextAlign.RIGHT,
            font_family="Consolas",
            weight=ft.FontWeight.BOLD,
        )
        
        self.width = 380
        self.bgcolor = "#0a0a0f"
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.border = ft.border.all(2, "#08f7fe")
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color="#08f7fe33",
        )
        
        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(controls=[self.formula_display], alignment="end"),
                            ft.Row(controls=[self.result], alignment="end"),
                        ],
                        spacing=5,
                    ),
                    padding=ft.padding.only(bottom=10),
                    border=ft.border.only(bottom=ft.BorderSide(1, "#08f7fe33")),
                ),
                ft.Row(
                    controls=[
                        ScientificButton(text="sin", button_clicked=self.button_clicked),
                        ScientificButton(text="cos", button_clicked=self.button_clicked),
                        ScientificButton(text="tan", button_clicked=self.button_clicked),
                        ScientificButton(text="π", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ScientificButton(text="√", button_clicked=self.button_clicked),
                        ScientificButton(text="x²", button_clicked=self.button_clicked),
                        ScientificButton(text="log", button_clicked=self.button_clicked),
                        ScientificButton(text="ln", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ScientificButton(text="(", button_clicked=self.button_clicked),
                        ScientificButton(text=")", button_clicked=self.button_clicked),
                        ScientificButton(text="^", button_clicked=self.button_clicked),
                        ScientificButton(text="e", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="⌫", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="÷", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="×", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked: {data}")
        
        if data == "AC":
            self.expression = ""
            self.result.value = "0"
            self.formula_display.value = ""
        
        elif data == "⌫":
            if self.expression:
                for func in ["sin(", "cos(", "tan(", "log(", "ln(", "sqrt("]:
                    if self.expression.endswith(func):
                        self.expression = self.expression[:-len(func)]
                        break
                else:
                    self.expression = self.expression[:-1]
                self.result.value = self.expression if self.expression else "0"
        
        elif data == "=":
            try:
                self.formula_display.value = self.expression
                result = self.evaluate_expression(self.expression)
                self.result.value = self.format_number(result)
                self.expression = self.result.value
            except Exception as ex:
                print(f"Calculation error: {ex}")
                self.result.value = "Error"
                self.expression = ""
        
        elif data in "0123456789.":
            self.expression += data
            self.result.value = self.expression
        
        elif data == "+":
            self.expression += "+"
            self.result.value = self.expression
        elif data == "-":
            self.expression += "-"
            self.result.value = self.expression
        elif data == "×":
            self.expression += "×"
            self.result.value = self.expression
        elif data == "÷":
            self.expression += "÷"
            self.result.value = self.expression
        elif data == "^":
            self.expression += "^"
            self.result.value = self.expression
        elif data == "%":
            self.expression += "%"
            self.result.value = self.expression
        
        elif data == "(":
            self.expression += "("
            self.result.value = self.expression
        elif data == ")":
            self.expression += ")"
            self.result.value = self.expression
        
        elif data == "sin":
            self.expression += "sin("
            self.result.value = self.expression
        elif data == "cos":
            self.expression += "cos("
            self.result.value = self.expression
        elif data == "tan":
            self.expression += "tan("
            self.result.value = self.expression
        elif data == "√":
            self.expression += "sqrt("
            self.result.value = self.expression
        elif data == "log":
            self.expression += "log("
            self.result.value = self.expression
        elif data == "ln":
            self.expression += "ln("
            self.result.value = self.expression
        
        elif data == "x²":
            self.expression += "^2"
            self.result.value = self.expression
        
        elif data == "π":
            self.expression += "π"
            self.result.value = self.expression
        elif data == "e":
            self.expression += "e"
            self.result.value = self.expression
        
        self.update()

    def evaluate_expression(self, expr):
        if not expr:
            return 0
        
        calc_expr = expr
        calc_expr = calc_expr.replace("×", "*")
        calc_expr = calc_expr.replace("÷", "/")
        calc_expr = calc_expr.replace("^", "**")
        calc_expr = calc_expr.replace("π", str(math.pi))
        calc_expr = calc_expr.replace("e", str(math.e))
        calc_expr = calc_expr.replace("%", "/100")
        
        calc_expr = calc_expr.replace("sin(", "math.sin(")
        calc_expr = calc_expr.replace("cos(", "math.cos(")
        calc_expr = calc_expr.replace("tan(", "math.tan(")
        calc_expr = calc_expr.replace("sqrt(", "math.sqrt(")
        calc_expr = calc_expr.replace("log(", "math.log10(")
        calc_expr = calc_expr.replace("ln(", "math.log(")
        
        print(f"Evaluating: {calc_expr}")
        
        allowed_names = {
            "math": math,
            "abs": abs,
            "round": round,
        }
        
        result = eval(calc_expr, {"__builtins__": {}}, allowed_names)
        return result

    def format_number(self, num):
        if isinstance(num, str):
            return num
        if num == int(num):
            return str(int(num))
        return f"{num:.10g}"


def main(page: ft.Page):
    page.title = "NEON CALC"
    page.window.width = 420
    page.window.height = 700
    page.bgcolor = "#0a0a0f"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    calc = CalculatorApp()
    page.add(calc)


ft.app(main)