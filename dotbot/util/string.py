def indent_lines(string, amount=2, delimiter="\n"):
    whitespace = " " * amount
    sep = "%s%s" % (delimiter, whitespace)
    return "%s%s" % (whitespace, sep.join(string.split(delimiter)))
