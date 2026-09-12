"""Conservative chemistry notation formatting for --chem mode."""

import re


SUBSCRIPT = str.maketrans("0123456789+-", "₀₁₂₃₄₅₆₇₈₉₊₋")
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
}


def _number(value: str) -> str:
    return NUMBER_WORDS.get(value.lower(), value)


def _format_orbital(match: re.Match[str]) -> str:
    principal = _number(match.group("principal"))
    orbital = match.group("orbital").lower()
    electrons = _number(match.group("electrons"))
    return f"{principal}{orbital}{electrons.translate(SUPERSCRIPT)}"


def _format_ion(match: re.Match[str]) -> str:
    element = match.group("element")
    charge = _number(match.group("charge")).translate(SUPERSCRIPT)
    sign = "⁺" if match.group("sign").lower() == "plus" else "⁻"
    return f"{element}{charge}{sign}"


def _format_element_count(match: re.Match[str]) -> str:
    return f"{match.group('element')}{_number(match.group('count')).translate(SUBSCRIPT)}"


def _subscript_formula_digits(match: re.Match[str]) -> str:
    return f"{match.group('element')}{match.group('count').translate(SUBSCRIPT)}"


def format_chemistry(text: str) -> str:
    """Format only explicit chemistry phrases; leave other caption text intact."""
    formatted = text

    # Thermodynamics and standard-state notation.
    formatted = re.sub(r"\bdelta\s+g\s+naught\b", "ΔG°", formatted, flags=re.I)
    formatted = re.sub(r"\bdelta\s+h\s+naught\b", "ΔH°", formatted, flags=re.I)
    formatted = re.sub(r"\bdelta\s+s\s+naught\b", "ΔS°", formatted, flags=re.I)
    formatted = re.sub(r"\bdelta\s+([gGhHsS])\b", lambda m: f"Δ{m.group(1).upper()}", formatted)
    formatted = re.sub(r"\bg\s+naught\b", "G°", formatted, flags=re.I)
    formatted = re.sub(r"\bh\s+naught\b", "H°", formatted, flags=re.I)

    # Explicit electron-configuration terms: "one s two" -> "1s²".
    formatted = re.sub(
        r"\b(?P<principal>\d+|one|two|three|four|five|six|seven)"
        r"\s*(?P<orbital>[spdf])\s*"
        r"(?P<electrons>\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten)\b",
        _format_orbital,
        formatted,
        flags=re.I,
    )

    # Explicit ion notation: "Fe three plus" -> "Fe³⁺".
    formatted = re.sub(
        r"\b(?P<element>[A-Z][a-z]?)\s+"
        r"(?P<charge>\d+|one|two|three|four|five|six)"
        r"\s+(?P<sign>plus|minus)\b",
        _format_ion,
        formatted,
    )

    # Formula notation deliberately requires a chemical symbol, avoiding word rewrites.
    formatted = re.sub(
        r"\b(?P<element>[A-Z][a-z]?)\s+"
        r"(?P<count>\d+|zero|one|two|three|four|five|six|seven|eight|nine)\b",
        _format_element_count,
        formatted,
    )
    formatted = re.sub(
        r"(?P<element>[A-Z][a-z]?)(?P<count>\d+)",
        _subscript_formula_digits,
        formatted,
    )

    # Common chemistry units and equation language.
    formatted = re.sub(r"\bkilojoules?\s+per\s+mole\b", "kJ mol⁻¹", formatted, flags=re.I)
    formatted = re.sub(r"\bjoules?\s+per\s+mole\s+kelvin\b", "J mol⁻¹ K⁻¹", formatted, flags=re.I)
    formatted = re.sub(r"\bmoles?\s+per\s+liter\b", "mol L⁻¹", formatted, flags=re.I)
    formatted = re.sub(r"\b(is in equilibrium with|is at equilibrium with)\b", "⇌", formatted, flags=re.I)
    formatted = re.sub(r"\b(yields|produces|reacts to form)\b", "→", formatted, flags=re.I)
    formatted = re.sub(r"\bequals\b", "=", formatted, flags=re.I)
    formatted = re.sub(r"\s+([=→⇌])\s+", r" \1 ", formatted)

    return formatted
