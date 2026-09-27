# from __future__ import annotations
#
# import sys
# from pathlib import Path
# from typing import Iterable
#
# from PIL import Image
#
# # Dark -> light. Use denser characters for more detail.
# CHARS = "@%#*+=-:. "
#
#
# def rgb_to_ansi(r: int, g: int, b: int) -> str:
#     return f"\x1b[38;2;{r};{g};{b}m"
#
#
# def clamp(n: int, lo: int, hi: int) -> int:
#     return max(lo, min(hi, n))
#
#
# def image_to_ascii(path: str | Path, width: int = 100) -> Iterable[str]:
#     img = Image.open(path).convert("RGB")
#
#     # Terminal characters are taller than they are wide, so we compensate.
#     w, h = img.size
#     aspect = h / w
#     height = max(1, int(width * aspect * 0.5))
#     img = img.resize((width, height))
#
#     px = img.load()
#     for y in range(height):
#         line = []
#         for x in range(width):
#             r, g, b = px[x, y]
#             gray = int(0.299 * r + 0.587 * g + 0.114 * b)
#             idx = int(gray / 255 * (len(CHARS) - 1))
#             ch = CHARS[clamp(idx, 0, len(CHARS) - 1)]
#             line.append(f"{rgb_to_ansi(r, g, b)}{ch}")
#         line.append("\x1b[0m")
#         yield "".join(line)
#
#
# def main() -> None:
#     if len(sys.argv) < 2:
#         print("Usage: python terminal_color_ascii.py <image_path> [width]")
#         raise SystemExit(1)
#
#     path = sys.argv[1]
#     width = int(sys.argv[2]) if len(sys.argv) > 2 else 100
#
#     for line in image_to_ascii(path, width):
#         print(line)
#
#
# if __name__ == "__main__":
#     main()

print("[green]username[/]")
