"""
Color Converter — convert colours between HEX, RGB, and HSL formats.
"""

import argparse
import colorsys
import re
import sys

from devtoolkit.core.plugin import BaseTool


class ColorConvTool(BaseTool):
    name = "colorconv"
    description = "在 HEX, RGB 與 HSL 顏色格式之間進行轉換"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "value", nargs="?", default=None,
            help='顏色數值，例如 "#ff8800", "rgb(255,136,0)", "hsl(32,100%%,50%%)"',
        )
        parser.add_argument(
            "--hex", default=None,
            help="輸入 HEX 格式 (例如 ff8800 或 #ff8800)",
        )
        parser.add_argument(
            "--rgb", nargs=3, type=int, metavar=("R", "G", "B"),
            help="輸入 RGB 數值 (0-255)",
        )
        parser.add_argument(
            "--hsl", nargs=3, type=float, metavar=("H", "S", "L"),
            help="輸入 HSL 格式 (H: 0-360, S: 0-100, L: 0-100)",
        )

    def run(self, args: argparse.Namespace) -> None:
        r, g, b = None, None, None

        if args.rgb:
            r, g, b = args.rgb
        elif args.hex:
            r, g, b = self._parse_hex(args.hex)
        elif args.hsl:
            r, g, b = self._hsl_to_rgb(args.hsl[0], args.hsl[1], args.hsl[2])
        elif args.color:
            r, g, b = self._auto_parse(args.color)
        else:
            print("Error: provide a colour value. See --help for formats.",
                  file=sys.stderr)
            sys.exit(1)

        if r is None:
            print("Error: could not parse colour input.", file=sys.stderr)
            sys.exit(1)

        # Clamp values
        r, g, b = (max(0, min(255, v)) for v in (r, g, b))

        # Convert to all formats
        hex_str = f"#{r:02x}{g:02x}{b:02x}"
        h, l_val, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        h_deg = round(h * 360)
        s_pct = round(s * 100)
        l_pct = round(l_val * 100)

        print(f"HEX:  {hex_str}")
        print(f"RGB:  rgb({r}, {g}, {b})")
        print(f"HSL:  hsl({h_deg}, {s_pct}%, {l_pct}%)")
        print(f"  R={r}  G={g}  B={b}")

    # ── helpers ────────────────────────────────────────────────

    @staticmethod
    def _parse_hex(raw: str) -> tuple:
        raw = raw.strip().lstrip("#")
        if len(raw) == 3:
            raw = "".join(c * 2 for c in raw)
        if len(raw) != 6:
            return None, None, None
        try:
            return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
        except ValueError:
            return None, None, None

    @staticmethod
    def _hsl_to_rgb(h: float, s: float, l: float) -> tuple:
        r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
        return round(r * 255), round(g * 255), round(b * 255)

    def _auto_parse(self, text: str) -> tuple:
        text = text.strip()
        # Try HEX
        if re.match(r"^#?[0-9a-fA-F]{3,6}$", text):
            return self._parse_hex(text)
        # Try rgb(...)
        m = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", text, re.I)
        if m:
            return int(m.group(1)), int(m.group(2)), int(m.group(3))
        # Try hsl(...)
        m = re.match(
            r"hsl\(\s*([\d.]+)\s*,\s*([\d.]+)%?\s*,\s*([\d.]+)%?\s*\)", text, re.I
        )
        if m:
            return self._hsl_to_rgb(float(m.group(1)), float(m.group(2)), float(m.group(3)))
        return None, None, None
