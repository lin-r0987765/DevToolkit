"""
Day 1 Tool: Pomodoro Timer
A simple countdown timer with Pomodoro Technique defaults.

Usage:
    devtoolkit timer               # 25-minute Pomodoro
    devtoolkit timer -m 5          # 5-minute custom timer
    devtoolkit timer -m 50 -l "Deep Work"
"""

import argparse
import time
import sys
from devtoolkit.core.plugin import BaseTool


class TimerTool(BaseTool):
    name = "timer"
    description = "🍅 Pomodoro countdown timer (default: 25 min)"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-m", "--minutes",
            type=float,
            default=25.0,
            metavar="MIN",
            help="Duration in minutes (default: 25)",
        )
        parser.add_argument(
            "-s", "--seconds",
            type=float,
            default=0.0,
            metavar="SEC",
            help="Additional seconds to add to the timer (default: 0)",
        )
        parser.add_argument(
            "-l", "--label",
            type=str,
            default="Pomodoro",
            metavar="LABEL",
            help='Session label (default: "Pomodoro")',
        )
        parser.add_argument(
            "--no-progress",
            action="store_true",
            help="Disable the live countdown display",
        )

    def run(self, args: argparse.Namespace) -> None:
        total_seconds = int(args.minutes * 60 + args.seconds)

        if total_seconds <= 0:
            print("Error: Timer duration must be greater than zero.", file=sys.stderr)
            sys.exit(1)

        label = args.label
        mins, secs = divmod(total_seconds, 60)

        print(f"\n⏱  [{label}] Timer started — {mins:02d}:{secs:02d} remaining")
        print("   Press Ctrl+C to cancel.\n")

        start = time.time()
        try:
            for remaining in range(total_seconds, 0, -1):
                m, s = divmod(remaining, 60)
                if not args.no_progress:
                    bar_len = 30
                    filled = bar_len - int(remaining / total_seconds * bar_len)
                    bar = "█" * filled + "░" * (bar_len - filled)
                    print(
                        f"\r   [{bar}] {m:02d}:{s:02d} remaining ",
                        end="",
                        flush=True,
                    )
                time.sleep(1)
        except KeyboardInterrupt:
            elapsed = int(time.time() - start)
            em, es = divmod(elapsed, 60)
            print(f"\n\n⚠️  Timer cancelled after {em:02d}:{es:02d}.")
            sys.exit(0)

        print(f"\n\n✅ [{label}] Time's up! Great work — take a well-deserved break. 🎉\n")
