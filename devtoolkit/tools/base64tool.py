# devtoolkit/tools/base64tool.py
"""Base64 Encoder / Decoder — encode and decode strings or files."""

import argparse
import base64
import sys

from devtoolkit.core.plugin import BaseTool


class Base64Tool(BaseTool):
    name = "base64tool"
    description = "Base64 編碼與解碼（支援字串及檔案）"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "input",
            nargs="?",
            default=None,
            help="要編碼/解碼的字串（也可透過 stdin 傳入）",
        )
        parser.add_argument(
            "-d", "--decode",
            action="store_true",
            help="解碼模式（預設為編碼）",
        )
        parser.add_argument(
            "-f", "--file",
            default=None,
            help="從檔案讀取輸入",
        )
        parser.add_argument(
            "-o", "--output",
            default=None,
            help="將結果寫入檔案（而非 stdout）",
        )
        parser.add_argument(
            "--urlsafe",
            action="store_true",
            help="使用 URL-safe Base64 字元集",
        )

    def run(self, args: argparse.Namespace) -> None:
        # Determine input data
        if args.file:
            try:
                with open(args.file, "rb") as f:
                    data = f.read()
            except FileNotFoundError:
                print(f"錯誤：找不到檔案 '{args.file}'")
                return
        elif args.input:
            data = args.input.encode("utf-8")
        elif not sys.stdin.isatty():
            data = sys.stdin.buffer.read()
        else:
            print("錯誤：請提供字串、--file 或從 stdin 傳入資料")
            return

        encode_fn = base64.urlsafe_b64encode if args.urlsafe else base64.b64encode
        decode_fn = base64.urlsafe_b64decode if args.urlsafe else base64.b64decode

        try:
            if args.decode:
                result = decode_fn(data)
            else:
                result = encode_fn(data)
        except Exception as e:
            print(f"錯誤：{e}")
            return

        if args.output:
            with open(args.output, "wb") as f:
                f.write(result)
            print(f"結果已寫入 {args.output}")
        else:
            # Try printing as text; fall back to raw bytes info
            try:
                print(result.decode("utf-8"))
            except UnicodeDecodeError:
                print(f"（二進位資料，共 {len(result)} bytes — 請用 -o 輸出到檔案）")
