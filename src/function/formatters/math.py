"""Conservative mathematical notation formatting for --math mode."""

import re


SUPERSCRIPT = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")
NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}


def _number(value: str) -> str:
    return NUMBER_WORDS.get(value.lower(), value)


def _power(match: re.Match[str]) -> str:
    return f"{match.group('base')}{_number(match.group('power')).translate(SUPERSCRIPT)}"


def _integral(match: re.Match[str]) -> str:
    lower = _number(match.group("lower"))
    upper = _number(match.group("upper"))
    return f"∫_{lower}^{upper} "


def format_mathematics(text: str) -> str:
    """Format clear spoken notation while avoiding inference of missing structure."""
    formatted = text

    formatted = re.sub(
        r"\b(?P<base>[A-Za-z])\s+(?P<power>squared|cubed)\b",
        lambda m: f"{m.group('base')}{'²' if m.group('power').lower() == 'squared' else '³'}",
        formatted,
        flags=re.I,
    )
    formatted = re.sub(
        r"\b(?P<base>[A-Za-z])\s+to\s+the\s+power\s+of\s+"
        r"(?P<power>\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten)\b",
        _power,
        formatted,
        flags=re.I,
    )
    formatted = re.sub(
        r"\bintegral\s+from\s+(?P<lower>\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten)"
        r"\s+to\s+(?P<upper>\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten)"
        r"\s+of\b",
        _integral,
        formatted,
        flags=re.I,
    )
    formatted = re.sub(r"\bsquare root of\s+([A-Za-z0-9]+)\b", r"√(\1)", formatted, flags=re.I)
    formatted = re.sub(r"\bd\s+([A-Za-z])\b", r"d\1", formatted)

    replacements = [
        (r"\bgreater than or equal to\b", "≥"),
        (r"\bless than or equal to\b", "≤"),
        (r"\bnot equal to\b", "≠"),
        (r"\bdivided by\b", "÷"),
        (r"\btimes\b", "×"),
        (r"\bplus or minus\b", "±"),
        (r"\bequals\b", "="),
        (r"\bpi\b", "π"),
    ]
    for pattern, replacement in replacements:
        formatted = re.sub(pattern, replacement, formatted, flags=re.I)

    return re.sub(r"\s+([=×÷±≥≤≠])\s+", r" \1 ", formatted)
