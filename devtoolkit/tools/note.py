"""
Day 9 Tool: Quick Note
Quickly save, list, and search notes stored in a local Markdown file.

Usage:
    devtoolkit note "Remember to update docs"   # Add a note
    devtoolkit note -l                          # List all notes
    devtoolkit note -s "update"                 # Search notes
    devtoolkit note --clear                     # Clear all notes
    devtoolkit note --file ~/my_notes.md "hi"  # Use custom file
"""

import argparse
import os
import sys
from datetime import datetime
from devtoolkit.core.plugin import BaseTool

DEFAULT_NOTE_FILE = os.path.expanduser("~/.devtoolkit_notes.md")


class NoteTool(BaseTool):
    name = "note"
    description = "📝 Quickly save and list notes in a local Markdown file"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "text",
            nargs="?",
            metavar="TEXT",
            help="Note text to add (omit to list notes)",
        )
        parser.add_argument(
            "-l", "--list",
            action="store_true",
            help="List all saved notes",
        )
        parser.add_argument(
            "-s", "--search",
            metavar="QUERY",
            help="Search notes by keyword (case-insensitive)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all saved notes",
        )
        parser.add_argument(
            "--file",
            metavar="FILE",
            default=DEFAULT_NOTE_FILE,
            help=f"Note file path (default: {DEFAULT_NOTE_FILE})",
        )

    def _read_notes(self, path: str) -> list[str]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as fh:
            return fh.readlines()

    def _write_line(self, path: str, line: str) -> None:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line)

    def run(self, args: argparse.Namespace) -> None:
        path = args.file

        # --clear
        if args.clear:
            if os.path.exists(path):
                os.remove(path)
                print("🗑️  All notes cleared.")
            else:
                print("📭 No notes file found — nothing to clear.")
            return

        # -s / --search
        if args.search:
            lines = self._read_notes(path)
            query = args.search.lower()
            matches = [ln.rstrip() for ln in lines if query in ln.lower()]
            if matches:
                print(f"\n🔍 Notes matching '{args.search}':\n")
                for i, m in enumerate(matches, 1):
                    print(f"  {i:>3}. {m}")
                print()
            else:
                print(f"🔍 No notes found matching '{args.search}'.")
            return

        # -l / --list  (or no args → also list)
        if args.list or args.text is None:
            lines = self._read_notes(path)
            entries = [ln.rstrip() for ln in lines if ln.strip()]
            if entries:
                print(f"\n📋 Saved notes ({len(entries)}):\n")
                for i, entry in enumerate(entries, 1):
                    print(f"  {i:>3}. {entry}")
                print()
            else:
                print("📭 No notes yet. Add one with: devtoolkit note \"your text\"")
            return

        # Add a new note
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        line = f"- [{timestamp}] {args.text}\n"
        self._write_line(path, line)
        print(f"✅ Note saved: {args.text}")
