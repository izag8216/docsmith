"""Example module demonstrating docsmith parsing capabilities."""


def greet(name: str, greeting: str = "Hello") -> str:
    """Generate a personalized greeting.

    Args:
        name: The person to greet.
        greeting: The greeting word to use. Defaults to "Hello".

    Returns:
        A personalized greeting string.
    """
    return f"{greeting}, {name}!"


def add_numbers(a: int, b: int) -> int:
    """Add two integers together.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        The sum of a and b.
    """
    return a + b


def process_data(data: list, iterations: int = 10) -> list:
    """Process data with a specified number of iterations.

    Parameters
    ----------
    data : list
        Input data to process.
    iterations : int
        Number of iterations to run. Default is 10.

    Returns
    -------
    list
        Processed data after all iterations.
    """
    result = data[:]
    for _ in range(iterations):
        result = [x * 2 for x in result]
    return result


class Calculator:
    """A simple calculator for basic arithmetic operations.

    This class provides methods for addition, subtraction,
    multiplication, and division.
    """

    def __init__(self):
        """Initialize the calculator with zero result."""
        self.result = 0
        self.history = []

    def add(self, a: int, b: int) -> int:
        """Add two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            The sum of a and b.
        """
        self.result = a + b
        self.history.append(f"add({a}, {b}) = {self.result}")
        return self.result

    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a.

        :param a: The minuend.
        :param b: The subtrahend.
        :returns: The difference a - b.
        """
        self.result = a - b
        self.history.append(f"subtract({a}, {b}) = {self.result}")
        return self.result

    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers.

        Args:
            x: First factor.
            y: Second factor.

        Returns:
            The product of x and y.
        """
        self.result = x * y
        self.history.append(f"multiply({x}, {y}) = {self.result}")
        return self.result

    def divide(self, dividend: int, divisor: int) -> float:
        """Divide dividend by divisor.

        Args:
            dividend: The number to be divided.
            divisor: The number to divide by.

        Returns:
            The quotient of dividend divided by divisor.

        Raises:
            ValueError: If divisor is zero.
        """
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        self.result = dividend / divisor
        self.history.append(f"divide({dividend}, {divisor}) = {self.result}")
        return self.result


def calculate_stats(numbers: list) -> dict:
    """Calculate basic statistics for a list of numbers.

    Parameters
    ----------
    numbers : list
        List of numbers to analyze.

    Returns
    -------
    dict
        Dictionary containing mean, median, and sum.

    Examples
    --------
    >>> calculate_stats([1, 2, 3, 4, 5])
    {'mean': 3.0, 'median': 3, 'sum': 15}
    """
    if not numbers:
        return {"mean": 0, "median": 0, "sum": 0}

    sorted_nums = sorted(numbers)
    n = len(sorted_nums)

    if n % 2 == 0:
        median = (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2
    else:
        median = sorted_nums[n // 2]

    return {
        "mean": sum(numbers) / n,
        "median": median,
        "sum": sum(numbers),
        "count": n,
    }