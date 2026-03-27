"""
Day 5 Tool: Hash Calculator
Compute cryptographic hashes for files or text strings.

Usage:
    devtoolkit hashit -t "hello world"           # SHA-256 of a string
    devtoolkit hashit -f myfile.zip              # SHA-256 of a file
    devtoolkit hashit -t "hello" -a md5          # MD5 of a string
    devtoolkit hashit -f myfile.zip --all        # All common hashes
    devtoolkit hashit -f a.zip --verify <hash>   # Verify a known hash
"""

import argparse
import hashlib
import sys
from devtoolkit.core.plugin import BaseTool

SUPPORTED = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512", "blake2b", "blake2s"]
CHUNK = 65536  # 64 KB read buffer


def _hash_bytes(data: bytes, algo: str) -> str:
    h = hashlib.new(algo)
    h.update(data)
    return h.hexdigest()


def _hash_file(path: str, algo: str) -> str:
    h = hashlib.new(algo)
    try:
        with open(path, "rb") as fh:
            while chunk := fh.read(CHUNK):
                h.update(chunk)
    except OSError as exc:
        print(f"❌ Cannot read file: {exc}", file=sys.stderr)
        sys.exit(1)
    return h.hexdigest()


class HashItTool(BaseTool):
    name = "hashit"
    description = "🔑 Compute cryptographic hashes for files or text strings"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        source = parser.add_mutually_exclusive_group(required=True)
        source.add_argument(
            "-f", "--file",
            metavar="FILE",
            help="Path to the file to hash",
        )
        source.add_argument(
            "-t", "--text",
            metavar="TEXT",
            help="Text string to hash (UTF-8 encoded)",
        )

        parser.add_argument(
            "-a", "--algo",
            choices=SUPPORTED,
            default="sha256",
            metavar="ALGO",
            help=f"Hash algorithm (default: sha256). Choices: {', '.join(SUPPORTED)}",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Compute all supported hash algorithms at once",
        )
        parser.add_argument(
            "--verify",
            metavar="HASH",
            help="Compare computed hash against this known value (case-insensitive)",
        )
        parser.add_argument(
            "--upper",
            action="store_true",
            help="Output hash in UPPERCASE",
        )

    def _compute(self, args: argparse.Namespace, algo: str) -> str:
        if args.file:
            digest = _hash_file(args.file, algo)
        else:
            digest = _hash_bytes(args.text.encode("utf-8"), algo)
        return digest.upper() if args.upper else digest

    def run(self, args: argparse.Namespace) -> None:
        label = args.file if args.file else f'"{args.text}"'

        if args.all:
            print(f"\n🔑 Hashes for {label}:\n")
            for algo in SUPPORTED:
                try:
                    digest = self._compute(args, algo)
                    print(f"   {algo:<10} {digest}")
                except ValueError:
                    print(f"   {algo:<10} (not supported on this platform)")
            print()
            return

        algo = args.algo
        digest = self._compute(args, algo)

        print(f"\n🔑 {algo.upper()} hash of {label}:\n")
        print(f"   {digest}\n")

        if args.verify:
            expected = args.verify.strip().lower()
            actual = digest.lower()
            if actual == expected:
                print("   ✅ Verification PASSED — hashes match.\n")
            else:
                print("   ❌ Verification FAILED — hashes do NOT match.")
                print(f"      Expected : {expected}")
                print(f"      Got      : {actual}\n")
                sys.exit(1)
