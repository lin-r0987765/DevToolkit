"""
Day 11 Tool: Base Converter
Convert integers between decimal, hexadecimal, binary, and octal.

Usage:
    devtoolkit baseconv 255               # Dec → hex, bin, oct
    devtoolkit baseconv 0xFF              # Hex → all bases
    devtoolkit baseconv 0b11111111        # Binary → all bases
    devtoolkit baseconv 255 -o hex        # Dec → hex only
    devtoolkit baseconv 255 -o bin        # Dec → binary only
    devtoolkit baseconv -i hex -o dec FF  # Explicit: hex → decimal
"""

import argparse
import sys
from devtoolkit.core.plugin import BaseTool

BASE_MAP = {
    "dec": 10,
    "hex": 16,
    "bin": 2,
    "oct": 8,
}

PREFIX_MAP = {
    "0x": "hex",
    "0X": "hex",
    "0b": "bin",
    "0B": "bin",
    "0o": "oct",
    "0O": "oct",
}

LABEL = {
    "dec": "Decimal   (base 10)",
    "hex": "Hex       (base 16)",
    "bin": "Binary    (base  2)",
    "oct": "Octal     (base  8)",
}


def _detect_base(value: str) -> tuple[int, str]:
    """Auto-detect the base from a string prefix and return (int_value, base_name)."""
    lower = value.lower()
    for prefix, base_name in PREFIX_MAP.items():
        if lower.startswith(prefix):
            digits = value[len(prefix):]
            return int(digits, BASE_MAP[base_name]), base_name
    # Plain number — assume decimal
    return int(value, 10), "dec"


def _format_value(n: int, base: str) -> str:
    if base == "dec":
        return str(n)
    if base == "hex":
        return hex(n)            # "0xff"
    if base == "bin":
        return bin(n)            # "0b11111111"
    if base == "oct":
        return oct(n)            # "0o377"
    raise ValueError(f"Unknown base: {base}")


class BaseConvTool(BaseTool):
    name = "baseconv"
    description = "🔢 Convert integers between decimal, hex, binary, and octal"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "value",
            metavar="VALUE",
            help=(
                "Integer to convert. Prefix determines base: "
                "0x/0X = hex, 0b/0B = binary, 0o/0O = octal, plain = decimal."
            ),
        )
        parser.add_argument(
            "-i", "--input-base",
            choices=list(BASE_MAP.keys()),
            metavar="BASE",
            help="Override input base (dec, hex, bin, oct). Default: auto-detect from prefix.",
        )
        parser.add_argument(
            "-o", "--output-base",
            choices=list(BASE_MAP.keys()),
            metavar="BASE",
            help="Output only this base. Default: show all bases.",
        )

    def run(self, args: argparse.Namespace) -> None:
        raw = args.value

        try:
            if args.input_base:
                n = int(raw, BASE_MAP[args.input_base])
                in_base = args.input_base
            else:
                n, in_base = _detect_base(raw)
        except ValueError:
            print(f"❌ Cannot parse '{raw}' as a valid integer.", file=sys.stderr)
            sys.exit(1)

        if args.output_base:
            result = _format_value(n, args.output_base)
            print(result)
            return

        print(f"\n🔢 Base conversion for {raw}  (detected input: {in_base})\n")
        for base in ("dec", "hex", "bin", "oct"):
            formatted = _format_value(n, base)
            print(f"   {LABEL[base]:<24}  {formatted}")
        print()
