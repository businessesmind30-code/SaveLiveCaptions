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
    "ten": "10",
}

ELEMENTS = {
    "H": "hydrogen", "He": "helium", "Li": "lithium", "Be": "beryllium",
    "B": "boron", "C": "carbon", "N": "nitrogen", "O": "oxygen",
    "F": "fluorine", "Ne": "neon", "Na": "sodium", "Mg": "magnesium",
    "Al": "aluminium", "Si": "silicon", "P": "phosphorus", "S": "sulfur",
    "Cl": "chlorine", "Ar": "argon", "K": "potassium", "Ca": "calcium",
    "Sc": "scandium", "Ti": "titanium", "V": "vanadium", "Cr": "chromium",
    "Mn": "manganese", "Fe": "iron", "Co": "cobalt", "Ni": "nickel",
    "Cu": "copper", "Zn": "zinc", "Ga": "gallium", "Ge": "germanium",
    "As": "arsenic", "Se": "selenium", "Br": "bromine", "Kr": "krypton",
    "Rb": "rubidium", "Sr": "strontium", "Y": "yttrium", "Zr": "zirconium",
    "Nb": "niobium", "Mo": "molybdenum", "Tc": "technetium", "Ru": "ruthenium",
    "Rh": "rhodium", "Pd": "palladium", "Ag": "silver", "Cd": "cadmium",
    "In": "indium", "Sn": "tin", "Sb": "antimony", "Te": "tellurium",
    "I": "iodine", "Xe": "xenon", "Cs": "cesium", "Ba": "barium",
    "La": "lanthanum", "Ce": "cerium", "Pr": "praseodymium", "Nd": "neodymium",
    "Pm": "promethium", "Sm": "samarium", "Eu": "europium", "Gd": "gadolinium",
    "Tb": "terbium", "Dy": "dysprosium", "Ho": "holmium", "Er": "erbium",
    "Tm": "thulium", "Yb": "ytterbium", "Lu": "lutetium", "Hf": "hafnium",
    "Ta": "tantalum", "W": "tungsten", "Re": "rhenium", "Os": "osmium",
    "Ir": "iridium", "Pt": "platinum", "Au": "gold", "Hg": "mercury",
    "Tl": "thallium", "Pb": "lead", "Bi": "bismuth", "Po": "polonium",
    "At": "astatine", "Rn": "radon", "Fr": "francium", "Ra": "radium",
    "Ac": "actinium", "Th": "thorium", "Pa": "protactinium", "U": "uranium",
    "Np": "neptunium", "Pu": "plutonium", "Am": "americium", "Cm": "curium",
    "Bk": "berkelium", "Cf": "californium", "Es": "einsteinium", "Fm": "fermium",
    "Md": "mendelevium", "No": "nobelium", "Lr": "lawrencium", "Rf": "rutherfordium",
    "Db": "dubnium", "Sg": "seaborgium", "Bh": "bohrium", "Hs": "hassium",
    "Mt": "meitnerium", "Ds": "darmstadtium", "Rg": "roentgenium", "Cn": "copernicium",
    "Nh": "nihonium", "Fl": "flerovium", "Mc": "moscovium", "Lv": "livermorium",
    "Ts": "tennessine", "Og": "oganesson",
}
ELEMENT_BY_UPPER = {symbol.upper(): symbol for symbol in ELEMENTS}
ELEMENT_BY_NAME = {name: symbol for symbol, name in ELEMENTS.items()}
ELEMENT_BY_NAME["aluminum"] = "Al"

NUMBER_PATTERN = r"\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten"
ELEMENT_PATTERN = "|".join(
    sorted((re.escape(symbol) for symbol in ELEMENTS), key=len, reverse=True)
)
ELEMENT_NAME_PATTERN = "|".join(
    sorted((re.escape(name) for name in ELEMENT_BY_NAME), key=len, reverse=True)
)


def _number(value: str) -> str:
    return NUMBER_WORDS.get(value.lower(), value)


def _format_orbital(match: re.Match[str]) -> str:
    principal = _number(match.group("principal"))
    orbital = match.group("orbital").lower()
    electrons = _number(match.group("electrons"))
    return f"{principal}{orbital}{electrons.translate(SUPERSCRIPT)}"


def _format_ion(element: str, charge: str, sign: str) -> str:
    charge_text = _number(charge).translate(SUPERSCRIPT)
    sign_text = "⁺" if sign.lower() == "plus" else "⁻"
    return f"{element}{charge_text}{sign_text}"


def _format_symbol_charge_last(match: re.Match[str]) -> str:
    return _format_ion(
        match.group("element"), match.group("charge"), match.group("sign")
    )


def _format_symbol_charge_first(match: re.Match[str]) -> str:
    return _format_ion(
        match.group("element"), match.group("charge"), match.group("sign")
    )


def _format_named_ion(match: re.Match[str]) -> str:
    element = ELEMENT_BY_NAME[match.group("element").lower()]
    return _format_ion(element, match.group("charge"), match.group("sign"))


def _format_element_count(match: re.Match[str]) -> str:
    return (
        f"{match.group('element')}"
        f"{_number(match.group('count')).translate(SUBSCRIPT)}"
    )


def _subscript_formula_digits(match: re.Match[str]) -> str:
    return f"{match.group('element')}{match.group('count').translate(SUBSCRIPT)}"


def _format_uppercase_symbol(match: re.Match[str]) -> str:
    """Normalize FE -> Fe only when the entire uppercase token is an element."""
    return ELEMENT_BY_UPPER.get(match.group(0), match.group(0))


def _format_spelled_polyatomic_ion(match: re.Match[str]) -> str:
    first = ELEMENT_BY_UPPER.get(match.group("first"))
    second = ELEMENT_BY_UPPER.get(match.group("second"))
    if first is None or second is None:
        return match.group(0)

    formula = f"{first}{second}{_number(match.group('subscript')).translate(SUBSCRIPT)}"
    return _format_ion(formula, match.group("charge"), match.group("sign"))


def format_chemistry(text: str) -> str:
    """Format only explicit chemistry phrases; leave other caption text intact."""
    formatted = text

    # Thermodynamics and standard-state notation.
    formatted = re.sub(r"\bdelta\s+g\s+naught\b", "ΔG°", formatted, flags=re.I)
    formatted = re.sub(r"\bdelta\s+h\s+naught\b", "ΔH°", formatted, flags=re.I)
    formatted = re.sub(r"\bdelta\s+s\s+naught\b", "ΔS°", formatted, flags=re.I)
    formatted = re.sub(
        r"\bdelta\s+([gGhHsS])\b",
        lambda match: f"Δ{match.group(1).upper()}",
        formatted,
    )
    formatted = re.sub(r"\bg\s+naught\b", "G°", formatted, flags=re.I)
    formatted = re.sub(r"\bh\s+naught\b", "H°", formatted, flags=re.I)

    # Explicit electron-configuration terms: "one s two" -> "1s²".
    formatted = re.sub(
        rf"\b(?P<principal>{NUMBER_PATTERN})\s*(?P<orbital>[spdf])\s*"
        rf"(?P<electrons>{NUMBER_PATTERN})\b",
        _format_orbital,
        formatted,
        flags=re.I,
    )

    # "S O four two minus" -> "SO₄²⁻".
    formatted = re.sub(
        rf"\b(?P<first>[A-Z])\s+(?P<second>[A-Z])\s+"
        rf"(?P<subscript>{NUMBER_PATTERN})\s+"
        rf"(?P<charge>{NUMBER_PATTERN})\s+(?P<sign>plus|minus)\b",
        _format_spelled_polyatomic_ion,
        formatted,
    )

    # FE -> Fe. Longer all-capital acronyms, e.g. MBBS, are not matched.
    formatted = re.sub(r"\b[A-Z]{1,2}\b", _format_uppercase_symbol, formatted)

    # "iron three plus" -> "Fe³⁺".
    formatted = re.sub(
        rf"\b(?P<element>{ELEMENT_NAME_PATTERN})\s+"
        rf"(?P<charge>{NUMBER_PATTERN})\s+(?P<sign>plus|minus)\b",
        _format_named_ion,
        formatted,
        flags=re.I,
    )

    # "Fe three plus" -> "Fe³⁺" and "Fe plus two" -> "Fe²⁺".
    formatted = re.sub(
        rf"\b(?P<element>{ELEMENT_PATTERN})\s+"
        rf"(?P<charge>{NUMBER_PATTERN})\s+(?P<sign>plus|minus)\b",
        _format_symbol_charge_last,
        formatted,
    )
    formatted = re.sub(
        rf"\b(?P<element>{ELEMENT_PATTERN})\s+"
        rf"(?P<sign>plus|minus)\s+(?P<charge>{NUMBER_PATTERN})\b",
        _format_symbol_charge_first,
        formatted,
    )

    # Formula notation requires a valid symbol, avoiding ordinary-word rewrites.
    formatted = re.sub(
        rf"\b(?P<element>{ELEMENT_PATTERN})\s+"
        rf"(?P<count>{NUMBER_PATTERN})\b",
        _format_element_count,
        formatted,
    )
    formatted = re.sub(
        r"(?P<element>[A-Z][a-z]?)(?P<count>\d+)",
        _subscript_formula_digits,
        formatted,
    )

    # Common chemistry units and equation language.
    formatted = re.sub(
        r"\bkilojoules?\s+per\s+mole\b", "kJ mol⁻¹", formatted, flags=re.I
    )
    formatted = re.sub(
        r"\bjoules?\s+per\s+mole\s+kelvin\b",
        "J mol⁻¹ K⁻¹",
        formatted,
        flags=re.I,
    )
    formatted = re.sub(
        r"\bmoles?\s+per\s+liter\b", "mol L⁻¹", formatted, flags=re.I
    )
    formatted = re.sub(
        r"\b(is in equilibrium with|is at equilibrium with)\b",
        "⇌",
        formatted,
        flags=re.I,
    )
    formatted = re.sub(
        r"\b(yields|produces|reacts to form)\b", "→", formatted, flags=re.I
    )
    formatted = re.sub(r"\bequals\b", "=", formatted, flags=re.I)
    formatted = re.sub(r"\s+([=→⇌])\s+", r" \1 ", formatted)

    return formatted
