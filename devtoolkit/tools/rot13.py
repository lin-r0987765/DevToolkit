"""
ROT13 Cipher — encode/decode text using the ROT13 substitution cipher.
"""

import argparse
import codecs
import sys

from devtoolkit.core.plugin import BaseTool


class Rot13Tool(BaseTool):
    name = "rot13"
    description = "使用 ROT13 (或自訂位移 N) 對文字進行編碼/解碼"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "text", nargs="?", default=None,
            help="要編碼/解碼的文字 (若省略則讀取 stdin)",
        )
        parser.add_argument(
            "-n", "--shift", type=int, default=13,
            help="位移量 (預設: 13)",
        )
        parser.add_argument(
            "-f", "--file", default=None,
            help="從檔案讀取輸入",
        )

    def run(self, args: argparse.Namespace) -> None:
        # Determine input source
        if args.file:
            try:
                with open(args.file, "r", encoding="utf-8") as fh:
                    text = fh.read()
            except FileNotFoundError:
                print(f"Error: file not found: {args.file}", file=sys.stderr)
                sys.exit(1)
        elif args.text:
            text = args.text
        elif not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            print("Error: provide text as an argument, via --file, or pipe to stdin.",
                  file=sys.stderr)
            sys.exit(1)

        shift = args.shift % 26
        if shift == 13:
            # Use Python's built-in ROT13 codec for the classic case
            result = codecs.encode(text, "rot_13")
        else:
            result = self._rotate(text, shift)

        print(result, end="")

    @staticmethod
    def _rotate(text: str, shift: int) -> str:
        """Apply a Caesar cipher with the given shift to ASCII letters."""
        out = []
        for ch in text:
            if "a" <= ch <= "z":
                out.append(chr((ord(ch) - ord("a") + shift) % 26 + ord("a")))
            elif "A" <= ch <= "Z":
                out.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
            else:
                out.append(ch)
        return "".join(out)
