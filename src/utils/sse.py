def string_to_sse(string: str, event: str | None = None) -> str:
    # Prefix every line with "data: "
    string="".join(f"data: {line}" for line in string.splitlines(keepends=True))
    # Add event name if given
    if event is not None:
        string = f"event: {event}\n{string}"
    # Add double newline to indicate end of message
    string += "\n\n"
    return string
