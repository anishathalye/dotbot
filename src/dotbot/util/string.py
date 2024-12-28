def indent_lines(string: str, amount: int = 2, delimiter: str = "\n") -> str:
    whitespace = " " * amount
    sep = f"{delimiter}{whitespace}"
    return f"{whitespace}{sep.join(string.split(delimiter))}"
