"""Optional subject-specific caption formatters."""

from collections.abc import Callable


def get_formatter(mode: str | None) -> Callable[[str], str] | None:
    """Load a formatter only when its matching command-line mode is selected."""
    if mode == "chem":
        from .chem import format_chemistry

        return format_chemistry
    if mode == "math":
        from .math import format_mathematics

        return format_mathematics
    if mode == "physics":
        from .physics import format_physics

        return format_physics
    return None
