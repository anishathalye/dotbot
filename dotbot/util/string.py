def indent_lines(string, amount=2, delimiter="\n"):
    whitespace = " " * amount
    sep = f"{delimiter}{whitespace}"
    return f"{whitespace}{sep.join(string.split(delimiter))}"
