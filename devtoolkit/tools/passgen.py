"""
Day 3 Tool: Password Generator
Generates cryptographically secure random passwords with configurable options.

Usage:
    devtoolkit passgen                    # 16-char password (default)
    devtoolkit passgen -l 32              # 32-char password
    devtoolkit passgen -n 5               # Generate 5 passwords
    devtoolkit passgen --no-symbols       # Letters and digits only
    devtoolkit passgen --no-upper         # Lowercase + digits + symbols
    devtoolkit passgen --pin 6            # 6-digit numeric PIN
"""

import argparse
import secrets
import string
import sys
from devtoolkit.core.plugin import BaseTool


class PassgenTool(BaseTool):
    name = "passgen"
    description = "🔐 Generate cryptographically secure random passwords"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-l", "--length",
            type=int,
            default=16,
            metavar="N",
            help="Password length (default: 16)",
        )
        parser.add_argument(
            "-n", "--count",
            type=int,
            default=1,
            metavar="N",
            help="Number of passwords to generate (default: 1)",
        )
        parser.add_argument(
            "--no-upper",
            action="store_true",
            help="Exclude uppercase letters",
        )
        parser.add_argument(
            "--no-lower",
            action="store_true",
            help="Exclude lowercase letters",
        )
        parser.add_argument(
            "--no-digits",
            action="store_true",
            help="Exclude digits",
        )
        parser.add_argument(
            "--no-symbols",
            action="store_true",
            help="Exclude special symbols",
        )
        parser.add_argument(
            "--pin",
            type=int,
            metavar="DIGITS",
            help="Generate a numeric PIN of the given length (overrides other flags)",
        )

    def run(self, args: argparse.Namespace) -> None:
        # PIN mode — pure numeric
        if args.pin is not None:
            if args.pin < 1:
                print("❌ PIN length must be at least 1.", file=sys.stderr)
                sys.exit(1)
            print(f"\n🔢 PIN ({args.pin} digits):\n")
            for _ in range(max(1, args.count)):
                pin = "".join(secrets.choice(string.digits) for _ in range(args.pin))
                print(f"   {pin}")
            print()
            return

        # Build character pool
        pool = ""
        if not args.no_upper:
            pool += string.ascii_uppercase
        if not args.no_lower:
            pool += string.ascii_lowercase
        if not args.no_digits:
            pool += string.digits
        if not args.no_symbols:
            pool += string.punctuation

        if not pool:
            print("❌ Character pool is empty — enable at least one character class.", file=sys.stderr)
            sys.exit(1)

        if args.length < 1:
            print("❌ Password length must be at least 1.", file=sys.stderr)
            sys.exit(1)

        count = max(1, args.count)
        print(f"\n🔐 Generated password{'s' if count > 1 else ''} (length={args.length}):\n")
        for _ in range(count):
            password = "".join(secrets.choice(pool) for _ in range(args.length))
            print(f"   {password}")
        print()

        # Entropy estimate (informational)
        import math
        entropy = args.length * math.log2(len(pool))
        print(f"   ℹ️  Pool size: {len(pool)} chars  |  Entropy: ~{entropy:.0f} bits\n")
