import re


def build_flags(ignore_case: bool, multiline: bool, dotall: bool) -> int:
    """Construit les flags pour re.compile en fonction des options cochées."""
    flags = 0  # On commence sans aucune option.

    # Option : ignorer majuscule/minuscule.
    if ignore_case:
        flags |= re.IGNORECASE

    # Option : autoriser les recherches sur plusieurs lignes.
    if multiline:
        flags |= re.MULTILINE

    # Option : permettre au . de capturer les retours à la ligne.
    if dotall:
        flags |= re.DOTALL

    return flags
