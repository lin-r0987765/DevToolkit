# devtoolkit/tools/uuidgen.py
"""UUID Generator — generate various versions of UUIDs."""

import argparse
import uuid

from devtoolkit.core.plugin import BaseTool


class UUIDGenTool(BaseTool):
    name = "uuidgen"
    description = "產生 UUID（支援 v1/v4/v5）"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-v", "--version",
            choices=["1", "4", "5"],
            default="4",
            help="UUID 版本：1（時間戳）、4（隨機，預設）、5（SHA-1 命名空間）",
        )
        parser.add_argument(
            "-n", "--count",
            type=int,
            default=1,
            help="一次產生幾組 UUID（預設 1）",
        )
        parser.add_argument(
            "--upper",
            action="store_true",
            help="以大寫輸出",
        )
        parser.add_argument(
            "--ns",
            choices=["dns", "url", "oid", "x500"],
            default="dns",
            help="UUID v5 的命名空間（預設 dns）",
        )
        parser.add_argument(
            "--name",
            default="",
            help="UUID v5 的名稱字串",
        )

    def run(self, args: argparse.Namespace) -> None:
        ns_map = {
            "dns": uuid.NAMESPACE_DNS,
            "url": uuid.NAMESPACE_URL,
            "oid": uuid.NAMESPACE_OID,
            "x500": uuid.NAMESPACE_X500,
        }

        for _ in range(args.count):
            if args.version == "1":
                result = uuid.uuid1()
            elif args.version == "5":
                if not args.name:
                    print("錯誤：UUID v5 需要 --name 參數")
                    return
                result = uuid.uuid5(ns_map[args.ns], args.name)
            else:
                result = uuid.uuid4()

            output = str(result)
            if args.upper:
                output = output.upper()
            print(output)
