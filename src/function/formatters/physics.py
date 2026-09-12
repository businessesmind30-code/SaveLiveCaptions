"""Physics notation formatting for --physics mode."""

import re

from .math import format_mathematics


def format_physics(text: str) -> str:
    """Apply physics-specific notation after the conservative math formatter."""
    formatted = format_mathematics(text)

    exact_equations = [
        (r"\bforce\s*=\s*mass\s*×\s*acceleration\b", "F = ma"),
        (r"\benergy\s*=\s*mass\s*c²\b", "E = mc²"),
        (r"\bpressure\s*=\s*force\s*/\s*area\b", "P = F/A"),
    ]
    for pattern, replacement in exact_equations:
        formatted = re.sub(pattern, replacement, formatted, flags=re.I)

    units = [
        (r"\bmeters?\s+per\s+second\s+squared\b", "m s⁻²"),
        (r"\bmeters?\s+per\s+second\b", "m s⁻¹"),
        (r"\bkilograms?\b", "kg"),
        (r"\bnewtons?\b", "N"),
        (r"\bjoules?\b", "J"),
        (r"\bwatts?\b", "W"),
        (r"\bkelvin\b", "K"),
    ]
    for pattern, replacement in units:
        formatted = re.sub(pattern, replacement, formatted, flags=re.I)

    greek = [
        (r"\bdelta\b", "Δ"),
        (r"\blambda\b", "λ"),
        (r"\bomega\b", "ω"),
        (r"\btheta\b", "θ"),
        (r"\brho\b", "ρ"),
        (r"\bmu\b", "μ"),
    ]
    for pattern, replacement in greek:
        formatted = re.sub(pattern, replacement, formatted, flags=re.I)

    return formatted
