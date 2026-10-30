"""Terminal output helpers shared by the chat integration.

``out`` prints text after making it safe for the Windows ``cp1252`` console,
so box-drawing characters and arrows never raise ``UnicodeEncodeError``.
"""


def safe(text: str) -> str:
    """Make ``text`` printable on a ``cp1252`` console.

    Box-drawing and arrow characters are first transliterated to ASCII; any
    remaining unencodable character is replaced with ``?`` rather than raising.

    Args:
        text: Text that may contain non-cp1252 characters.

    Returns:
        Text that can always be encoded as ``cp1252``.
    """
    # Transliterate the glyphs the game uses that cp1252 cannot encode.
    table = str.maketrans({"─": "-", "═": "=", "•": "*", "→": "->", "←": "<-"})
    text = text.translate(table)
    try:
        text.encode("cp1252")
        return text
    except UnicodeEncodeError:
        return text.encode("cp1252", errors="replace").decode("cp1252")


def out(text: str = "", end: str | None = None) -> None:
    """Print ``text`` after making it safe for the console encoding.

    Args:
        text: Text to print.
        end: Line terminator passed to ``print``; ``None`` means the default newline.
    """
    import builtins

    builtins.print(safe(text), end=end)
