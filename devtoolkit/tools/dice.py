"""Dice Roller — roll dice using tabletop RPG notation (e.g. 2d6, 1d20+5)."""

import argparse
import random
import re
from devtoolkit.core.plugin import BaseTool


class DiceTool(BaseTool):
    name = "dice"
    description = "Roll dice using RPG notation (e.g. 2d6, 1d20+5, 4d6kh3)"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("expression", nargs="?", default="1d6",
                            help="Dice expression: NdS[+/-M] or NdS[kh/kl]K (default: 1d6)")
        parser.add_argument("-n", "--repeat", type=int, default=1,
                            help="Roll the expression N times (default: 1)")
        parser.add_argument("-s", "--stats", action="store_true",
                            help="Show sum, min, max, and average after multiple rolls")
        parser.add_argument("--seed", type=int, default=None,
                            help="Set random seed for reproducible results")

    def run(self, args: argparse.Namespace) -> None:
        if args.seed is not None:
            random.seed(args.seed)

        expr = args.expression.lower().replace(" ", "")
        results = []

        for i in range(args.repeat):
            try:
                total, detail = self._evaluate(expr)
            except ValueError as e:
                print(f"Error: {e}")
                return

            results.append(total)
            if args.repeat == 1:
                print(f"  🎲 {args.expression} → {detail} = {total}")
            else:
                print(f"  Roll {i + 1:>3}: {detail} = {total}")

        if args.stats and len(results) > 1:
            print()
            print(f"  Rolls:   {len(results)}")
            print(f"  Sum:     {sum(results)}")
            print(f"  Min:     {min(results)}")
            print(f"  Max:     {max(results)}")
            print(f"  Average: {sum(results) / len(results):.2f}")

    def _evaluate(self, expr: str) -> tuple[int, str]:
        """Parse and evaluate a dice expression like 2d6+3 or 4d6kh3."""
        # Pattern: [N]d<S>[kh<K>|kl<K>][+/-<M>]
        pattern = r'^(\d*)d(\d+)(?:(kh|kl)(\d+))?([+-]\d+)?$'
        match = re.match(pattern, expr)
        if not match:
            raise ValueError(
                f"Invalid dice expression: '{expr}'. "
                "Use format like 2d6, 1d20+5, 4d6kh3"
            )

        num_dice = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        keep_mode = match.group(3)  # 'kh' or 'kl' or None
        keep_count = int(match.group(4)) if match.group(4) else None
        modifier = int(match.group(5)) if match.group(5) else 0

        if num_dice < 1 or num_dice > 100:
            raise ValueError("Number of dice must be between 1 and 100")
        if sides < 2 or sides > 1000:
            raise ValueError("Number of sides must be between 2 and 1000")
        if keep_count is not None and keep_count > num_dice:
            raise ValueError(f"Cannot keep {keep_count} dice when only rolling {num_dice}")

        # Roll the dice
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        detail_parts = []

        if keep_mode:
            sorted_rolls = sorted(rolls, reverse=(keep_mode == "kh"))
            kept = sorted_rolls[:keep_count]
            dropped = sorted_rolls[keep_count:]
            detail_parts.append(
                "[" + ", ".join(
                    f"{r}" if r in kept else f"~{r}~"
                    for r in rolls
                ) + "]"
            )
            total = sum(kept)
        else:
            detail_parts.append("[" + ", ".join(str(r) for r in rolls) + "]")
            total = sum(rolls)

        if modifier != 0:
            sign = "+" if modifier > 0 else ""
            detail_parts.append(f"{sign}{modifier}")
            total += modifier

        return total, " ".join(detail_parts)
