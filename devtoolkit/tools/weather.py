"""
Day 2 Tool: Weather Lookup
Fetches current weather using the free wttr.in API — no API key required.

Usage:
    devtoolkit weather                    # Weather in Taipei (default)
    devtoolkit weather -c Tokyo
    devtoolkit weather -c "New York" -f 3 # format 3: one-liner
    devtoolkit weather --full             # Full ASCII art forecast
"""

import argparse
import sys
import urllib.request
import urllib.error
import urllib.parse
from devtoolkit.core.plugin import BaseTool


# wttr.in format codes
FORMATS = {
    1: "%C",                        # Condition only
    2: "%C %t",                     # Condition + temperature
    3: "%l:+%c+%C+%t+%h+%w",       # One-liner (city, icon, condition, temp, humidity, wind)
    4: "%l: %c %C, %t (feels %f), humidity %h, wind %w",  # Full one-liner
}


class WeatherTool(BaseTool):
    name = "weather"
    description = "🌤  透過 wttr.in 查詢任何城市的天氣 (無需 API 金鑰)"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-c", "--city",
            type=str,
            default="Taipei",
            metavar="CITY",
            help='要查詢的城市名稱 (預設: "Taipei")',
        )
        parser.add_argument(
            "-f", "--format",
            type=int,
            choices=[1, 2, 3, 4],
            default=4,
            metavar="FORMAT",
            help=(
                "Output format (1–4, default: 4):\n"
                "  1 = condition only\n"
                "  2 = condition + temperature\n"
                "  3 = compact one-liner\n"
                "  4 = full one-liner (default)"
            ),
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="顯示完整的 ASCII 藝術天氣預報 (忽略 --format)",
        )
        parser.add_argument(
            "--lang",
            type=str,
            default="en",
            metavar="LANG",
            help="回覆語言代碼 (預設: en)，例如 zh, ja, fr",
        )

    def run(self, args: argparse.Namespace) -> None:
        city = urllib.parse.quote(args.city)

        if args.full:
            url = f"https://wttr.in/{city}?lang={args.lang}"
        else:
            fmt = FORMATS.get(args.format, FORMATS[4])
            encoded_fmt = urllib.parse.quote(fmt)
            url = f"https://wttr.in/{city}?format={encoded_fmt}&lang={args.lang}"

        print(f"\n🌍 Fetching weather for \"{args.city}\" ...\n")

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "DevToolkit/0.1 (curl-compatible)"},
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode("utf-8").strip()
        except urllib.error.URLError as exc:
            print(f"❌ Network error: {exc.reason}", file=sys.stderr)
            sys.exit(1)
        except Exception as exc:
            print(f"❌ Unexpected error: {exc}", file=sys.stderr)
            sys.exit(1)

        if args.full:
            print(data)
        else:
            # Clean up the compact format output for readability
            display = data.replace("+", " ").strip()
            print(f"   {display}\n")
