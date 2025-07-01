def remove_empty_lines(text: str) -> str:
    """
    Remove empty or whitespace-only lines from a paragraph.

    Args:
        text: The input string, potentially containing blank lines.

    Returns:
        A string with all empty lines removed.
    """
    # Split into lines, filter out lines that are empty after stripping whitespace,
    # then re-join with the original newline separator.
    non_empty_lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(non_empty_lines)



