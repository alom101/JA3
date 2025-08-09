from src.tools import Tool, ToolProperty

class CalculatorTool(Tool):
    def __init__(self):
        operation = ToolProperty(
            name="operation",
            _type="text",
            description="The operation to perform ('add', 'subtract', 'multiply', 'divide')",
            required=True,
            enum=["add", "subtract", "multiply", "divide"]
        )
        num1 = ToolProperty("num1", "float", "First number", True)
        num2 = ToolProperty("num2", "float", "Second number", True)
        super().__init__("calculator", "Prerforms a basic arithmetic operation between two numbers", [operation, num1, num2])

    def run(self, operation, num1, num2, *args, **kwargs):
        num1 = float(num1)
        num2 = float(num2)
        if operation == 'add':
            return num1 + num2
        elif operation == 'subtract':
            return num1 - num2
        elif operation == 'multiply':
            return num1 * num2
        elif operation == 'divide':
            if num2 == 0:
                raise ValueError("Cannot divide by zero.")
            return num1 / num2
        else:
            return "Invalid operation. Choose from 'add', 'subtract', 'multiply', 'divide'."
