"""Lorem Ipsum Generator — generate placeholder text for design and development."""

import argparse
import random
from devtoolkit.core.plugin import BaseTool

# Classic lorem ipsum vocabulary
_WORDS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua enim ad minim veniam "
    "quis nostrud exercitation ullamco laboris nisi aliquip ex ea commodo "
    "consequat duis aute irure in reprehenderit voluptate velit esse cillum "
    "fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt "
    "culpa qui officia deserunt mollit anim id est laborum porta nibh venenatis "
    "cras pulvinar mattis nunc blandit volutpat maecenas pharetra convallis "
    "posuere morbi leo urna molestie at elementum eu facilisis viverra neque "
    "aliquam vestibulum lectus mauris ultrices eros diam donec adipiscing "
    "tristique risus nec feugiat pretium fusce accumsan lacus vel facilisi "
    "nullam vehicula sagittis mauris pellentesque pulvinar habitant senectus "
    "netus fames turpis egestas integer eget aliquet bibendum enim facilisis "
    "gravida neque convallis cras semper auctor sapien faucibus et molestie ac"
).split()

_FIRST_SENTENCE = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
    "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
)


class LoremTool(BaseTool):
    name = "lorem"
    description = "Generate lorem ipsum placeholder text (words, sentences, or paragraphs)"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-w", "--words", type=int, default=0, metavar="N",
                            help="Generate exactly N words")
        parser.add_argument("-s", "--sentences", type=int, default=0, metavar="N",
                            help="Generate exactly N sentences")
        parser.add_argument("-p", "--paragraphs", type=int, default=0, metavar="N",
                            help="Generate N paragraphs (default: 1)")
        parser.add_argument("--no-classic", action="store_true",
                            help="Don't start with the classic 'Lorem ipsum dolor sit amet...'")
        parser.add_argument("--seed", type=int, default=None,
                            help="Random seed for reproducible output")
        parser.add_argument("--copy", action="store_true",
                            help="Print without trailing newline (useful for piping)")

    def run(self, args: argparse.Namespace) -> None:
        rng = random.Random(args.seed)
        classic = not args.no_classic

        if args.words > 0:
            text = self._gen_words(rng, args.words, classic)
        elif args.sentences > 0:
            text = self._gen_sentences(rng, args.sentences, classic)
        else:
            count = args.paragraphs if args.paragraphs > 0 else 1
            text = self._gen_paragraphs(rng, count, classic)

        if args.copy:
            print(text, end="")
        else:
            print(text)

    def _pick_words(self, rng: random.Random, n: int) -> list[str]:
        return [rng.choice(_WORDS) for _ in range(n)]

    def _gen_sentence(self, rng: random.Random) -> str:
        length = rng.randint(6, 15)
        words = self._pick_words(rng, length)
        words[0] = words[0].capitalize()
        # Occasionally insert a comma
        if length > 8:
            pos = rng.randint(3, length - 3)
            words[pos] = words[pos] + ","
        return " ".join(words) + "."

    def _gen_words(self, rng: random.Random, n: int, classic: bool) -> str:
        if classic and n >= 5:
            # Start with classic opening words
            opening = "Lorem ipsum dolor sit amet".split()
            if n <= len(opening):
                return " ".join(opening[:n])
            rest = self._pick_words(rng, n - len(opening))
            return " ".join(opening + rest)
        return " ".join(self._pick_words(rng, n))

    def _gen_sentences(self, rng: random.Random, n: int, classic: bool) -> str:
        sentences = []
        for i in range(n):
            if i == 0 and classic:
                sentences.append(_FIRST_SENTENCE)
            else:
                sentences.append(self._gen_sentence(rng))
        return " ".join(sentences)

    def _gen_paragraphs(self, rng: random.Random, n: int, classic: bool) -> str:
        paragraphs = []
        for i in range(n):
            num_sentences = rng.randint(4, 8)
            use_classic = classic and i == 0
            para = self._gen_sentences(rng, num_sentences, use_classic)
            paragraphs.append(para)
        return "\n\n".join(paragraphs)
