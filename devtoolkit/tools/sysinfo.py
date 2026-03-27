"""
System Info — display basic system and Python environment information.
"""

import argparse
import os
import platform
import shutil
import sys
import time

from devtoolkit.core.plugin import BaseTool


class SysInfoTool(BaseTool):
    name = "sysinfo"
    description = "Display system, Python, and disk information"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--disk", action="store_true",
            help="Show disk usage for common mount points",
        )
        parser.add_argument(
            "--python", action="store_true",
            help="Show Python environment details only",
        )
        parser.add_argument(
            "--json", action="store_true", dest="as_json",
            help="Output as JSON",
        )

    def run(self, args: argparse.Namespace) -> None:
        show_all = not args.disk and not args.python

        info = {}

        if show_all or args.python:
            info["python"] = self._python_info()

        if show_all:
            info["system"] = self._system_info()

        if show_all or args.disk:
            info["disk"] = self._disk_info()

        if args.as_json:
            import json
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            self._pretty_print(info)

    # ── data collectors ───────────────────────────────────────

    @staticmethod
    def _system_info() -> dict:
        uname = platform.uname()
        return {
            "OS": f"{uname.system} {uname.release}",
            "Machine": uname.machine,
            "Node": uname.node,
            "Processor": uname.processor or platform.processor() or "N/A",
            "Architecture": " / ".join(platform.architecture()),
            "Uptime": SysInfoTool._uptime(),
        }

    @staticmethod
    def _python_info() -> dict:
        return {
            "Version": platform.python_version(),
            "Implementation": platform.python_implementation(),
            "Compiler": platform.python_compiler(),
            "Executable": sys.executable,
            "Prefix": sys.prefix,
            "Path entries": len(sys.path),
        }

    @staticmethod
    def _disk_info() -> list:
        paths = ["/"] if os.name != "nt" else ["C:\\"]
        # Also check home directory if different mount
        home = os.path.expanduser("~")
        if home not in paths:
            paths.append(home)

        disks = []
        seen = set()
        for p in paths:
            try:
                usage = shutil.disk_usage(p)
            except (OSError, PermissionError):
                continue
            key = (usage.total, usage.free)
            if key in seen:
                continue
            seen.add(key)
            total_gb = usage.total / (1 << 30)
            used_gb = usage.used / (1 << 30)
            free_gb = usage.free / (1 << 30)
            pct = usage.used / usage.total * 100 if usage.total else 0
            disks.append({
                "path": p,
                "total": f"{total_gb:.1f} GB",
                "used": f"{used_gb:.1f} GB",
                "free": f"{free_gb:.1f} GB",
                "percent_used": f"{pct:.1f}%",
            })
        return disks

    @staticmethod
    def _uptime() -> str:
        try:
            with open("/proc/uptime", "r") as f:
                secs = float(f.read().split()[0])
        except (FileNotFoundError, PermissionError):
            return "N/A"
        days, rem = divmod(int(secs), 86400)
        hours, rem = divmod(rem, 3600)
        mins, _ = divmod(rem, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        parts.append(f"{mins}m")
        return " ".join(parts)

    # ── formatter ─────────────────────────────────────────────

    @staticmethod
    def _pretty_print(info: dict) -> None:
        if "system" in info:
            print("=== System ===")
            for k, v in info["system"].items():
                print(f"  {k:15s} {v}")
            print()

        if "python" in info:
            print("=== Python ===")
            for k, v in info["python"].items():
                print(f"  {k:15s} {v}")
            print()

        if "disk" in info:
            print("=== Disk ===")
            for d in info["disk"]:
                print(f"  {d['path']}")
                print(f"    Total: {d['total']}  Used: {d['used']}  "
                      f"Free: {d['free']}  ({d['percent_used']})")
