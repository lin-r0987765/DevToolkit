"""
Day 4 Tool: JSON Formatter & Validator
Pretty-prints, validates, and inspects JSON from a file or stdin.

Usage:
    devtoolkit jsonfmt data.json               # Pretty-print a file
    cat data.json | devtoolkit jsonfmt         # From stdin
    devtoolkit jsonfmt data.json --compact     # Minify JSON
    devtoolkit jsonfmt data.json --check       # Validate only (exit 0 = valid)
    devtoolkit jsonfmt data.json --keys        # List all top-level keys
    devtoolkit jsonfmt data.json --indent 2    # Custom indent width
"""

import argparse
import json
import sys
from devtoolkit.core.plugin import BaseTool


class JsonFmtTool(BaseTool):
    name = "jsonfmt"
    description = "📋 Pretty-print, validate, and inspect JSON files"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "file",
            nargs="?",
            metavar="FILE",
            help="Path to a JSON file (reads from stdin if omitted)",
        )
        parser.add_argument(
            "--indent",
            type=int,
            default=4,
            metavar="N",
            help="Indentation width (default: 4)",
        )
        parser.add_argument(
            "--compact",
            action="store_true",
            help="Output minified (compact) JSON instead of pretty-printing",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Validate JSON only; print result and exit with code 0 (valid) or 1 (invalid)",
        )
        parser.add_argument(
            "--keys",
            action="store_true",
            help="List top-level keys (object) or index count (array)",
        )
        parser.add_argument(
            "--sort-keys",
            action="store_true",
            help="Sort object keys alphabetically in the output",
        )

    def _load(self, args: argparse.Namespace):
        """Read and parse JSON from file or stdin."""
        try:
            if args.file:
                with open(args.file, "r", encoding="utf-8") as fh:
                    raw = fh.read()
                source = args.file
            else:
                raw = sys.stdin.read()
                source = "<stdin>"
        except OSError as exc:
            print(f"❌ Cannot read file: {exc}", file=sys.stderr)
            sys.exit(1)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            if args.check:
                print(f"❌ Invalid JSON — {exc}")
                sys.exit(1)
            print(f"❌ JSON parse error in {source}:\n   {exc}", file=sys.stderr)
            sys.exit(1)

        return data, source

    def run(self, args: argparse.Namespace) -> None:
        data, source = self._load(args)

        # --check mode
        if args.check:
            print(f"✅ Valid JSON  ({source})")
            return

        # --keys mode
        if args.keys:
            if isinstance(data, dict):
                keys = list(data.keys())
                print(f"\n🔑 Top-level keys in {source} ({len(keys)} total):\n")
                for k in keys:
                    val = data[k]
                    type_name = type(val).__name__
                    preview = ""
                    if isinstance(val, (str, int, float, bool)) or val is None:
                        preview = f" = {json.dumps(val)}"
                    elif isinstance(val, list):
                        preview = f" → list[{len(val)}]"
                    elif isinstance(val, dict):
                        preview = f" → dict[{len(val)} keys]"
                    print(f"   {k!r:<30} ({type_name}){preview}")
            elif isinstance(data, list):
                print(f"\n📦 {source} is a JSON array with {len(data)} item(s).")
                if data:
                    print(f"   First item type: {type(data[0]).__name__}")
            else:
                print(f"\n📄 {source} is a JSON scalar: {json.dumps(data)}")
            print()
            return

        # Pretty-print or compact
        if args.compact:
            output = json.dumps(data, separators=(",", ":"), ensure_ascii=False, sort_keys=args.sort_keys)
        else:
            output = json.dumps(data, indent=args.indent, ensure_ascii=False, sort_keys=args.sort_keys)

        print(output)
