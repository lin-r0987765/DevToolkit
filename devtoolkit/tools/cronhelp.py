"""
Day 10 Tool: Cron Helper
解析並以白話文解釋 cron 表達式.
Also list the next N scheduled run times.

Usage:
    devtoolkit cronhelp "* * * * *"          # Explain every-minute cron
    devtoolkit cronhelp "0 9 * * 1-5"        # 9 AM on weekdays
    devtoolkit cronhelp "0 0 1 * *" -n 5     # Next 5 run times
    devtoolkit cronhelp --examples            # Show common cron examples
"""

import argparse
import sys
from datetime import datetime, timedelta
from devtoolkit.core.plugin import BaseTool

FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]
MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}
DOW_NAMES = {
    0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
    4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday",
}

EXAMPLES = [
    ("* * * * *",       "Every minute"),
    ("0 * * * *",       "Every hour, on the hour"),
    ("0 9 * * *",       "Every day at 09:00"),
    ("0 9 * * 1-5",     "Every weekday (Mon–Fri) at 09:00"),
    ("0 0 * * 0",       "Every Sunday at midnight"),
    ("0 0 1 * *",       "First day of every month at midnight"),
    ("*/15 * * * *",    "Every 15 minutes"),
    ("0 0 * * 1",       "Every Monday at midnight"),
    ("30 18 * * 5",     "Every Friday at 18:30"),
    ("0 0 1 1 *",       "Once a year on January 1st at midnight"),
]


def _parse_field(field: str, min_val: int, max_val: int) -> list[int]:
    """Parse a single cron field and return the list of matching values."""
    result = set()
    for part in field.split(","):
        if part == "*":
            result.update(range(min_val, max_val + 1))
        elif "/" in part:
            range_part, step = part.split("/", 1)
            step = int(step)
            if range_part == "*":
                start, end = min_val, max_val
            elif "-" in range_part:
                start, end = map(int, range_part.split("-", 1))
            else:
                start = int(range_part)
                end = max_val
            result.update(range(start, end + 1, step))
        elif "-" in part:
            start, end = map(int, part.split("-", 1))
            result.update(range(start, end + 1))
        else:
            result.add(int(part))
    return sorted(v for v in result if min_val <= v <= max_val)


def _explain_field(field: str, field_name: str,
                   min_val: int, max_val: int,
                   name_map: dict | None = None) -> str:
    if field == "*":
        return f"every {field_name}"
    if field == "*/1":
        return f"every {field_name}"

    values = _parse_field(field, min_val, max_val)

    # Step pattern
    if field.startswith("*/"):
        step = field[2:]
        return f"every {step} {field_name}s"

    if name_map:
        named = [name_map.get(v, str(v)) for v in values]
    else:
        named = [str(v) for v in values]

    if len(named) == 1:
        return f"on {field_name} {named[0]}"
    if len(named) == 2:
        return f"on {field_name}s {named[0]} and {named[1]}"
    return f"on {field_name}s {', '.join(named[:-1])}, and {named[-1]}"


def _explain(expr: str) -> str:
    parts = expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Expected 5 fields, got {len(parts)}: '{expr}'")

    minute_f, hour_f, dom_f, month_f, dow_f = parts

    minute_desc = _explain_field(minute_f, "minute", 0, 59)
    hour_desc   = _explain_field(hour_f,   "hour",   0, 23)
    dom_desc    = _explain_field(dom_f,    "day",    1, 31)
    month_desc  = _explain_field(month_f,  "month",  1, 12, MONTH_NAMES)
    dow_desc    = _explain_field(dow_f,    "weekday",0,  7,  DOW_NAMES)

    # Build human sentence
    time_part = (
        "every minute" if minute_f == "*" and hour_f == "*"
        else f"at minute {minute_f}" if hour_f == "*"
        else f"at {_fmt_time(minute_f, hour_f)}"
    )

    if dom_f == "*" and dow_f == "*":
        day_part = f"{month_desc}" if month_f != "*" else "every day"
    elif dow_f != "*":
        day_part = f"{dow_desc}"
        if month_f != "*":
            day_part += f", {month_desc}"
    else:
        day_part = f"{dom_desc}"
        if month_f != "*":
            day_part += f", {month_desc}"

    return f"{time_part}, {day_part}"


def _fmt_time(minute_f: str, hour_f: str) -> str:
    """Format time portion when both fields are specific."""
    if "/" in minute_f or "*" in minute_f or "," in minute_f or "-" in minute_f:
        return f"{_explain_field(minute_f, 'minute', 0, 59)} past {_explain_field(hour_f, 'hour', 0, 23)}"
    if "/" in hour_f or "*" in hour_f or "," in hour_f or "-" in hour_f:
        return f"minute {minute_f} of {_explain_field(hour_f, 'hour', 0, 23)}"
    h = int(hour_f)
    m = int(minute_f)
    ampm = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12:02d}:{m:02d} {ampm}"


def _next_runs(expr: str, count: int) -> list[datetime]:
    """Compute the next `count` run times after now (minute-resolution)."""
    parts = expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Expected 5 fields, got {len(parts)}")

    minute_f, hour_f, dom_f, month_f, dow_f = parts
    minutes  = _parse_field(minute_f, 0, 59)
    hours    = _parse_field(hour_f,   0, 23)
    days     = _parse_field(dom_f,    1, 31)
    months   = _parse_field(month_f,  1, 12)
    dows     = _parse_field(dow_f,    0, 7)
    dows_set = {d % 7 for d in dows}

    runs = []
    dt = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=1)
    limit = dt + timedelta(days=366 * 5)

    while len(runs) < count and dt < limit:
        if (dt.month in months
                and dt.day in days
                and (dow_f == "*" or dt.weekday() + 1 % 7 in dows_set
                     or dt.isoweekday() % 7 in dows_set)
                and dt.hour in hours
                and dt.minute in minutes):
            runs.append(dt)
        dt += timedelta(minutes=1)
    return runs


class CronHelpTool(BaseTool):
    name = "cronhelp"
    description = "⏰ 解析並以白話文解釋 cron 表達式"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "expression",
            nargs="?",
            metavar="EXPRESSION",
            help='包含在引號內的 Cron 表達式，例如 "0 9 * * 1-5"',
        )
        parser.add_argument(
            "-n", "--next",
            metavar="N",
            type=int,
            default=0,
            help="顯示接下來的 N 次預定執行時間 (預設: 0)",
        )
        parser.add_argument(
            "--examples",
            action="store_true",
            help="顯示常見 cron 範列表格",
        )

    def run(self, args: argparse.Namespace) -> None:
        if args.examples:
            print("\n📅 Common cron expressions:\n")
            print(f"  {'Expression':<20} Description")
            print(f"  {'-'*20} {'-'*35}")
            for expr, desc in EXAMPLES:
                print(f"  {expr:<20} {desc}")
            print()
            return

        if not args.expression:
            print("❌ Please provide a cron expression or use --examples.", file=sys.stderr)
            print('   Usage: devtoolkit cronhelp "0 9 * * 1-5"', file=sys.stderr)
            sys.exit(1)

        expr = args.expression
        try:
            explanation = _explain(expr)
        except ValueError as exc:
            print(f"❌ Invalid cron expression: {exc}", file=sys.stderr)
            sys.exit(1)

        print(f"\n⏰ Cron expression: {expr}\n")
        print(f"   Meaning:  {explanation.capitalize()}\n")

        if args.next > 0:
            try:
                runs = _next_runs(expr, args.next)
            except Exception as exc:
                print(f"❌ Could not compute next runs: {exc}", file=sys.stderr)
                sys.exit(1)

            print(f"   Next {args.next} scheduled run(s):\n")
            for i, dt in enumerate(runs, 1):
                print(f"      {i:>3}. {dt.strftime('%Y-%m-%d %H:%M')}")
            print()
