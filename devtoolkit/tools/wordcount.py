"""Word Count — count words, lines, and characters in text or files."""

import argparse
import sys
import os
from devtoolkit.core.plugin import BaseTool


class WordCountTool(BaseTool):
    name = "wordcount"
    description = "Count words, lines, characters, and sentences in text or files"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("file", nargs="?", default=None,
                            help="File to analyze (reads stdin if omitted)")
        parser.add_argument("-t", "--text", default=None,
                            help="Analyze a string directly")
        parser.add_argument("--chars", action="store_true",
                            help="Show only character count")
        parser.add_argument("--words", action="store_true",
                            help="Show only word count")
        parser.add_argument("--lines", action="store_true",
                            help="Show only line count")
        parser.add_argument("--sentences", action="store_true",
                            help="Show only sentence count")
        parser.add_argument("--freq", type=int, default=0, metavar="N",
                            help="Show top N most frequent words")

    def run(self, args: argparse.Namespace) -> None:
        # Get input text
        if args.text:
            text = args.text
        elif args.file:
            if not os.path.isfile(args.file):
                print(f"Error: file not found: {args.file}", file=sys.stderr)
                sys.exit(1)
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            if sys.stdin.isatty():
                print("Reading from stdin (Ctrl+D to finish)...", file=sys.stderr)
            text = sys.stdin.read()

        # Compute statistics
        num_chars = len(text)
        num_chars_no_space = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
        words = text.split()
        num_words = len(words)
        lines = text.splitlines()
        num_lines = len(lines)
        # Simple sentence detection: split on .!?
        sentences = [s.strip() for s in self._split_sentences(text) if s.strip()]
        num_sentences = len(sentences)

        # Filtered output
        specific = args.chars or args.words or args.lines or args.sentences
        if specific:
            if args.lines:
                print(num_lines)
            if args.words:
                print(num_words)
            if args.chars:
                print(num_chars)
            if args.sentences:
                print(num_sentences)
        else:
            print(f"  Lines:                {num_lines:>10,}")
            print(f"  Words:                {num_words:>10,}")
            print(f"  Characters:           {num_chars:>10,}")
            print(f"  Characters (no space):{num_chars_no_space:>10,}")
            print(f"  Sentences:            {num_sentences:>10,}")
            if num_words > 0 and num_sentences > 0:
                avg = num_words / num_sentences
                print(f"  Avg words/sentence:   {avg:>10.1f}")

        # Word frequency
        if args.freq > 0:
            freq: dict[str, int] = {}
            for w in words:
                clean = w.strip(".,!?;:\"'()[]{}<>").lower()
                if clean:
                    freq[clean] = freq.get(clean, 0) + 1
            top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[: args.freq]
            print(f"\n  Top {args.freq} words:")
            for word, count in top:
                print(f"    {word:<20s} {count:>6,}")

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split text on sentence-ending punctuation."""
        import re
        return re.split(r'[.!?]+', text)
