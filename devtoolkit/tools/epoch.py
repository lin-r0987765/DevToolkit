# devtoolkit/tools/epoch.py
"""Epoch — Unix timestamp converter and current time display."""

import argparse
import time
from datetime import datetime, timezone, timedelta

from devtoolkit.core.plugin import BaseTool


class EpochTool(BaseTool):
    name = "epoch"
    description = "Unix 時間戳轉換工具（時間戳 ↔ 可讀時間）"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "timestamp",
            nargs="?",
            default=None,
            help="要轉換的 Unix 時間戳（整數或小數）；不給則顯示目前時間",
        )
        parser.add_argument(
            "-r", "--reverse",
            default=None,
            help="將可讀時間轉為 Unix 時間戳（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）",
        )
        parser.add_argument(
            "--utc",
            action="store_true",
            help="以 UTC 顯示（預設為本地時區）",
        )
        parser.add_argument(
            "--tz",
            type=float,
            default=None,
            help="指定 UTC 偏移量（小時），例如 8 代表 UTC+8",
        )
        parser.add_argument(
            "--ms",
            action="store_true",
            help="將輸入視為毫秒級時間戳",
        )

    def run(self, args: argparse.Namespace) -> None:
        # Determine target timezone
        if args.tz is not None:
            tz = timezone(timedelta(hours=args.tz))
            tz_label = f"UTC{'+' if args.tz >= 0 else ''}{args.tz:g}"
        elif args.utc:
            tz = timezone.utc
            tz_label = "UTC"
        else:
            tz = None  # local
            tz_label = "本地時間"

        # Mode 1: reverse — human-readable → timestamp
        if args.reverse:
            self._reverse(args.reverse, tz, tz_label)
            return

        # Mode 2: convert timestamp → human-readable
        if args.timestamp is not None:
            try:
                ts = float(args.timestamp)
            except ValueError:
                print(f"錯誤：'{args.timestamp}' 不是有效的時間戳")
                return
            if args.ms:
                ts /= 1000.0
            self._show(ts, tz, tz_label)
            return

        # Mode 3: show current time
        now = time.time()
        print(f"目前 Unix 時間戳：{int(now)}")
        print(f"毫秒級：{int(now * 1000)}")
        if tz:
            dt = datetime.fromtimestamp(now, tz=tz)
        else:
            dt = datetime.fromtimestamp(now)
        print(f"{tz_label}：{dt.strftime('%Y-%m-%d %H:%M:%S')}")

    def _show(self, ts: float, tz, tz_label: str) -> None:
        try:
            if tz:
                dt = datetime.fromtimestamp(ts, tz=tz)
            else:
                dt = datetime.fromtimestamp(ts)
        except (OSError, ValueError):
            print("錯誤：時間戳超出可轉換範圍")
            return

        print(f"Unix 時間戳：{int(ts)}")
        print(f"{tz_label}：{dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"ISO 8601 ：{dt.isoformat()}")
        print(f"星期　　　：{dt.strftime('%A')}")

    def _reverse(self, text: str, tz, tz_label: str) -> None:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(text, fmt)
                break
            except ValueError:
                continue
        else:
            print("錯誤：格式不正確，請使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS")
            return

        if tz:
            dt = dt.replace(tzinfo=tz)

        ts = dt.timestamp()
        print(f"輸入時間：{text}")
        print(f"Unix 時間戳：{int(ts)}")
        print(f"毫秒級：{int(ts * 1000)}")
