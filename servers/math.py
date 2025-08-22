from mcp.server import Server
from mcp.interface import tool
import math

class MathServer(Server):
    @tool
    def add(self, a: float, b: float) -> float:
        """Add two numbers together.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The sum of a and b
        """
        return a + b

    @tool
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a.
        
        Args:
            a: The minuend
            b: The subtrahend
            
        Returns:
            The difference between a and b
        """
        return a - b

    @tool
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers.
        
        Args:
            a: First factor
            b: Second factor
            
        Returns:
            The product of a and b
        """
        return a * b

    @tool
    def divide(self, a: float, b: float) -> float:
        """Divide a by b.
        
        Args:
            a: The dividend
            b: The divisor (must not be zero)
            
        Returns:
            The quotient of a divided by b
            
        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    @tool
    def power(self, base: float, exponent: float) -> float:
        """Raise base to the power of exponent.
        
        Args:
            base: The base number
            exponent: The exponent
            
        Returns:
            base raised to the power of exponent
        """
        return base ** exponent

    @tool
    def square_root(self, x: float) -> float:
        """Calculate the square root of a number.
        
        Args:
            x: The number (must be non-negative)
            
        Returns:
            The square root of x
            
        Raises:
            ValueError: If x is negative
        """
        if x < 0:
            raise ValueError("Cannot calculate square root of a negative number")
        return math.sqrt(x)

if __name__ == "__main__":
    server = MathServer()
    server.run()