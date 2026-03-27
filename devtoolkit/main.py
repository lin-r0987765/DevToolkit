"""
DevToolkit CLI Entry Point

Auto-discovers and loads all tools from devtoolkit/tools/.
Add a new tool by simply dropping a .py file in the tools/ directory
with a class that inherits from BaseTool.
"""

import argparse
import importlib
import inspect
import pkgutil
import sys
from pathlib import Path

# Make sure the package root is importable when running directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from devtoolkit.core.plugin import BaseTool
import devtoolkit.tools as tools_package


BANNER = """
╔══════════════════════════════════════╗
║          🛠  DevToolkit              ║
║  A plugin-based CLI toolkit          ║
║  Adding one tool every day           ║
╚══════════════════════════════════════╝
"""


def discover_tools() -> dict[str, BaseTool]:
    """
    Dynamically discover all BaseTool subclasses inside devtoolkit/tools/.
    Returns a dict mapping tool name -> tool instance.
    """
    discovered: dict[str, BaseTool] = {}

    for finder, module_name, is_pkg in pkgutil.iter_modules(tools_package.__path__):
        full_module = f"devtoolkit.tools.{module_name}"
        try:
            module = importlib.import_module(full_module)
        except Exception as exc:
            print(f"[warn] Could not load {full_module}: {exc}", file=sys.stderr)
            continue

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, BaseTool)
                and obj is not BaseTool
                and obj.name  # must have a name defined
            ):
                instance = obj()
                discovered[instance.name] = instance

    return discovered


def build_parser(tools: dict[str, BaseTool]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="devtoolkit",
        description="A plugin-based CLI toolkit — one new tool every day.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run `devtoolkit <tool> --help` for tool-specific options.",
    )

    subparsers = parser.add_subparsers(dest="tool", metavar="<tool>")

    for name, tool in sorted(tools.items()):
        sub = subparsers.add_parser(name, help=tool.description)
        tool.add_arguments(sub)

    return parser


def main() -> None:
    tools = discover_tools()

    if not tools:
        print("No tools found. Add a tool to devtoolkit/tools/ to get started.")
        sys.exit(1)

    parser = build_parser(tools)
    args = parser.parse_args()

    if args.tool is None:
        print(BANNER)
        parser.print_help()
        sys.exit(0)

    tool = tools[args.tool]
    tool.run(args)


if __name__ == "__main__":
    main()
