# 🛠 DevToolkit

> **A plugin-based Python CLI toolkit — one new tool added every day.**

DevToolkit is a personal productivity CLI built around a simple idea: ship one useful tool every day. The plugin architecture makes it trivially easy to add new tools — just drop a single Python file into the `tools/` directory and DevToolkit auto-discovers it.

---

## ✨ Features

- **Zero-config plugin system** — tools are auto-discovered at startup
- **Extensible** — add a new tool in minutes with a clean base class
- **No heavy dependencies** — uses Python's standard library wherever possible
- **Cross-platform** — works on macOS, Linux, and Windows

---

## 📦 Installation

**Requirements:** Python 3.10+

```bash
# Clone the repo
git clone https://github.com/r0987765/devtoolkit.git
cd devtoolkit

# Install in editable mode (recommended for development)
pip install -e .

# Or install directly
pip install .
```

After installation the `devtoolkit` command is available globally:

```bash
devtoolkit --help
```

---

## 🚀 Usage

### List all available tools

```bash
devtoolkit --help
```

### Run a specific tool

```bash
devtoolkit <tool> [options]
devtoolkit <tool> --help   # tool-specific help
```

---

## 🔧 Available Tools

| Day | Tool | Command | Description |
|-----|------|---------|-------------|
| Day 1 | 🍅 Pomodoro Timer | `devtoolkit timer` | Countdown timer with Pomodoro defaults (25 min) |
| Day 2 | 🌤 Weather | `devtoolkit weather` | Live weather lookup via wttr.in — no API key needed |
| Day 3 | 🔐 Password Generator | `devtoolkit passgen` | Cryptographically secure password & PIN generator |
| Day 4 | 📋 JSON Formatter | `devtoolkit jsonfmt` | Pretty-print, minify, validate, and inspect JSON |
| Day 5 | 🔑 Hash Calculator | `devtoolkit hashit` | Compute MD5/SHA/BLAKE2 hashes for files or strings |
| Day 6 | 🆔 UUID 產生器 | `devtoolkit uuidgen` | 產生 UUID v1/v4/v5，支援大寫與批次輸出 |
| Day 7 | 🔄 Base64 編解碼 | `devtoolkit base64tool` | Base64 編碼與解碼，支援字串、檔案與 URL-safe 模式 |
| Day 8 | ⏱ 時間戳轉換 | `devtoolkit epoch` | Unix 時間戳與可讀時間互轉，支援時區與毫秒 |
| Day 9 | 📝 Quick Note | `devtoolkit note` | Save, list, and search notes in a local Markdown file |
| Day 10 | ⏰ Cron Helper | `devtoolkit cronhelp` | Parse and explain cron expressions in plain language |
| Day 11 | 🔢 Base Converter | `devtoolkit baseconv` | Convert integers between decimal, hex, binary, and octal |
| Day 12 | 📊 Word Count | `devtoolkit wordcount` | Count words, lines, characters, and sentences in text or files |
| Day 13 | 🎲 Dice Roller | `devtoolkit dice` | Roll dice using RPG notation (e.g. 2d6, 1d20+5, 4d6kh3) |
| Day 14 | 📝 Lorem Ipsum | `devtoolkit lorem` | Generate lorem ipsum placeholder text for design and development |
| Day 15 | 🔤 ROT13 Cipher | `devtoolkit rot13` | Encode/decode text with ROT13 or custom rotation shift |
| Day 16 | 🎨 Color Converter | `devtoolkit colorconv` | Convert colours between HEX, RGB, and HSL formats |
| Day 17 | 💻 System Info | `devtoolkit sysinfo` | Display system, Python, and disk usage information |

### `timer` — Pomodoro Timer

```bash
devtoolkit timer                          # 25-minute Pomodoro (default)
devtoolkit timer -m 5                     # 5-minute timer
devtoolkit timer -m 50 -l "Deep Work"     # Custom duration + label
devtoolkit timer -s 90                    # 90-second timer
devtoolkit timer --no-progress            # Suppress live progress bar
```

| Flag | Default | Description |
|------|---------|-------------|
| `-m`, `--minutes` | `25` | Duration in minutes |
| `-s`, `--seconds` | `0` | Extra seconds to add |
| `-l`, `--label` | `Pomodoro` | Session label shown in output |
| `--no-progress` | off | Disable live countdown bar |

### `weather` — Weather Lookup

```bash
devtoolkit weather                        # Taipei (default)
devtoolkit weather -c Tokyo              # Another city
devtoolkit weather -c "New York" -f 3   # Compact one-liner format
devtoolkit weather --full                # Full ASCII art 3-day forecast
devtoolkit weather -c London --lang zh  # Chinese output
```

| Flag | Default | Description |
|------|---------|-------------|
| `-c`, `--city` | `Taipei` | City to look up |
| `-f`, `--format` | `4` | Output format 1–4 (see below) |
| `--full` | off | Show full ASCII art forecast |
| `--lang` | `en` | Language code (e.g. `zh`, `ja`, `fr`) |

**Format options:**

| Code | Output example |
|------|---------------|
| `1` | `Partly cloudy` |
| `2` | `Partly cloudy +22°C` |
| `3` | `Taipei: ⛅ Partly cloudy +22°C 72% ↗ 15km/h` |
| `4` | `Taipei: ⛅ Partly cloudy, +22°C (feels +21°C), humidity 72%, wind ↗ 15km/h` |

### `passgen` — Password Generator

```bash
devtoolkit passgen                         # 16-char password (default)
devtoolkit passgen -l 32                   # 32-char password
devtoolkit passgen -n 5                    # Generate 5 passwords
devtoolkit passgen --no-symbols            # Letters + digits only
devtoolkit passgen --no-upper --no-lower   # Digits + symbols only
devtoolkit passgen --pin 6                 # 6-digit numeric PIN
```

| Flag | Default | Description |
|------|---------|-------------|
| `-l`, `--length` | `16` | Password length |
| `-n`, `--count` | `1` | Number of passwords to generate |
| `--no-upper` | off | Exclude uppercase letters |
| `--no-lower` | off | Exclude lowercase letters |
| `--no-digits` | off | Exclude digits |
| `--no-symbols` | off | Exclude special symbols |
| `--pin DIGITS` | — | Generate a numeric PIN of given length |

### `jsonfmt` — JSON Formatter & Validator

```bash
devtoolkit jsonfmt data.json               # Pretty-print
cat data.json | devtoolkit jsonfmt         # From stdin
devtoolkit jsonfmt data.json --compact     # Minify JSON
devtoolkit jsonfmt data.json --check       # Validate only
devtoolkit jsonfmt data.json --keys        # List top-level keys
devtoolkit jsonfmt data.json --sort-keys   # Sort keys alphabetically
```

| Flag | Default | Description |
|------|---------|-------------|
| `FILE` | stdin | JSON file path (optional) |
| `--indent N` | `4` | Indentation width |
| `--compact` | off | Output minified JSON |
| `--check` | off | Validate only; exit 0 = valid, 1 = invalid |
| `--keys` | off | Show top-level keys with type info |
| `--sort-keys` | off | Sort object keys alphabetically |

### `hashit` — Hash Calculator

```bash
devtoolkit hashit -t "hello world"           # SHA-256 of a string (default)
devtoolkit hashit -f myfile.zip              # SHA-256 of a file
devtoolkit hashit -t "hello" -a md5          # MD5 hash
devtoolkit hashit -f myfile.zip --all        # All supported algorithms
devtoolkit hashit -f myfile.zip --verify abc123  # Verify against known hash
```

| Flag | Default | Description |
|------|---------|-------------|
| `-f`, `--file FILE` | — | File to hash |
| `-t`, `--text TEXT` | — | String to hash (UTF-8) |
| `-a`, `--algo ALGO` | `sha256` | Algorithm: md5, sha1, sha224, sha256, sha384, sha512, blake2b, blake2s |
| `--all` | off | Compute all algorithms at once |
| `--verify HASH` | — | Compare against a known hash (exit 1 on mismatch) |
| `--upper` | off | Output hash in UPPERCASE |

### `uuidgen` — UUID 產生器

```bash
devtoolkit uuidgen                         # 產生一組 UUID v4（預設）
devtoolkit uuidgen -n 5                    # 一次產生 5 組
devtoolkit uuidgen -v 1                    # UUID v1（時間戳）
devtoolkit uuidgen -v 5 --name example.com # UUID v5（命名空間 SHA-1）
devtoolkit uuidgen --upper                 # 大寫輸出
```

| Flag | Default | Description |
|------|---------|-------------|
| `-v`, `--version` | `4` | UUID 版本：1、4、5 |
| `-n`, `--count` | `1` | 產生數量 |
| `--upper` | off | 大寫輸出 |
| `--ns` | `dns` | v5 命名空間：dns、url、oid、x500 |
| `--name` | — | v5 名稱字串 |

### `base64tool` — Base64 編解碼

```bash
devtoolkit base64tool "Hello World"        # 編碼字串
devtoolkit base64tool -d "SGVsbG8gV29ybGQ=" # 解碼
devtoolkit base64tool -f image.png          # 編碼檔案
devtoolkit base64tool -d -f data.b64 -o out.bin  # 解碼並輸出到檔案
devtoolkit base64tool --urlsafe "Hello"     # URL-safe 編碼
```

| Flag | Default | Description |
|------|---------|-------------|
| `INPUT` | stdin | 要編碼/解碼的字串 |
| `-d`, `--decode` | off | 解碼模式 |
| `-f`, `--file` | — | 從檔案讀取 |
| `-o`, `--output` | — | 輸出到檔案 |
| `--urlsafe` | off | URL-safe Base64 |

### `epoch` — 時間戳轉換

```bash
devtoolkit epoch                            # 顯示目前時間戳
devtoolkit epoch 1700000000                 # 轉換為可讀時間
devtoolkit epoch 1700000000000 --ms         # 毫秒級時間戳
devtoolkit epoch 1700000000 --utc           # 以 UTC 顯示
devtoolkit epoch 1700000000 --tz 8          # 以 UTC+8 顯示
devtoolkit epoch -r "2024-01-15 12:30:00"  # 可讀時間 → 時間戳
```

| Flag | Default | Description |
|------|---------|-------------|
| `TIMESTAMP` | — | Unix 時間戳（不給則顯示目前時間） |
| `-r`, `--reverse` | — | 可讀時間 → 時間戳 |
| `--utc` | off | 以 UTC 顯示 |
| `--tz` | — | UTC 偏移（小時） |
| `--ms` | off | 輸入為毫秒級時間戳 |

### `note` — Quick Note

```bash
devtoolkit note "Remember to update docs"   # Add a note
devtoolkit note -l                          # List all notes
devtoolkit note -s "update"                 # Search notes by keyword
devtoolkit note --clear                     # Delete all notes
devtoolkit note --file ~/my_notes.md "hi"  # Use a custom notes file
```

| Flag | Default | Description |
|------|---------|-------------|
| `TEXT` | — | Note text to save |
| `-l`, `--list` | off | List all saved notes |
| `-s`, `--search QUERY` | — | Search notes by keyword (case-insensitive) |
| `--clear` | off | Delete all saved notes |
| `--file FILE` | `~/.devtoolkit_notes.md` | Custom notes file path |

### `cronhelp` — Cron Expression Helper

```bash
devtoolkit cronhelp "* * * * *"          # Every minute
devtoolkit cronhelp "0 9 * * 1-5"        # Explain weekday schedule
devtoolkit cronhelp "0 0 1 * *" -n 5     # Show next 5 run times
devtoolkit cronhelp --examples            # Show common cron patterns
```

| Flag | Default | Description |
|------|---------|-------------|
| `EXPRESSION` | — | Cron expression in quotes |
| `-n`, `--next N` | `0` | Show next N scheduled run times |
| `--examples` | off | Print a table of common cron expressions |

### `baseconv` — Base Converter

```bash
devtoolkit baseconv 255               # Decimal → hex, bin, oct
devtoolkit baseconv 0xFF              # Hex → all bases
devtoolkit baseconv 0b11111111        # Binary → all bases
devtoolkit baseconv 255 -o hex        # Output hex only
devtoolkit baseconv -i hex -o dec FF  # Explicit hex → decimal
```

| Flag | Default | Description |
|------|---------|-------------|
| `VALUE` | — | Integer to convert (prefix auto-detects base) |
| `-i`, `--input-base` | auto | Force input base: `dec`, `hex`, `bin`, `oct` |
| `-o`, `--output-base` | all | Output a single base: `dec`, `hex`, `bin`, `oct` |

### `wordcount` — Word Count

```bash
devtoolkit wordcount README.md             # Full stats for a file
cat essay.txt | devtoolkit wordcount       # From stdin
devtoolkit wordcount -t "Hello world"      # Analyze a string directly
devtoolkit wordcount README.md --words     # Word count only
devtoolkit wordcount README.md --freq 10   # Top 10 most frequent words
```

| Flag | Default | Description |
|------|---------|-------------|
| `FILE` | stdin | File to analyze (optional) |
| `-t`, `--text` | — | Analyze a string directly |
| `--chars` | off | Show only character count |
| `--words` | off | Show only word count |
| `--lines` | off | Show only line count |
| `--sentences` | off | Show only sentence count |
| `--freq N` | — | Show top N most frequent words |

### `dice` — Dice Roller

```bash
devtoolkit dice                   # Roll 1d6 (default)
devtoolkit dice 2d6               # Roll two six-sided dice
devtoolkit dice 1d20+5            # Roll with modifier
devtoolkit dice 4d6kh3            # Roll 4d6, keep highest 3 (D&D stats)
devtoolkit dice 1d20 -n 10 -s    # Roll 10 times with statistics
```

| Flag | Default | Description |
|------|---------|-------------|
| `EXPRESSION` | `1d6` | Dice expression: NdS[+/-M] or NdS[kh/kl]K |
| `-n`, `--repeat` | `1` | Roll the expression N times |
| `-s`, `--stats` | off | Show sum, min, max, average after multiple rolls |
| `--seed` | — | Random seed for reproducible results |

### `lorem` — Lorem Ipsum Generator

```bash
devtoolkit lorem                  # One paragraph (default)
devtoolkit lorem -p 3             # Three paragraphs
devtoolkit lorem -s 5             # Five sentences
devtoolkit lorem -w 50            # Exactly 50 words
devtoolkit lorem --no-classic     # Skip the classic opening
devtoolkit lorem -p 2 --copy     # No trailing newline (for piping)
```

| Flag | Default | Description |
|------|---------|-------------|
| `-w`, `--words` | — | Generate exactly N words |
| `-s`, `--sentences` | — | Generate exactly N sentences |
| `-p`, `--paragraphs` | `1` | Generate N paragraphs |
| `--no-classic` | off | Don't start with "Lorem ipsum dolor sit amet..." |
| `--seed` | — | Random seed for reproducible output |
| `--copy` | off | No trailing newline (useful for piping) |

### `rot13` — ROT13 Cipher

```bash
devtoolkit rot13 "Hello World"            # Encode with ROT13
devtoolkit rot13 "Uryyb Jbeyq"            # Decode (ROT13 is self-inverse)
devtoolkit rot13 -n 5 "Hello"             # Caesar cipher with shift 5
devtoolkit rot13 -f secret.txt            # Encode a file
echo "secret" | devtoolkit rot13          # From stdin
```

| Flag | Default | Description |
|------|---------|-------------|
| `TEXT` | stdin | Text to encode/decode |
| `-n`, `--shift` | `13` | Rotation shift amount (1–25) |
| `-f`, `--file` | — | Read input from a file |

### `colorconv` — Color Converter

```bash
devtoolkit colorconv "#ff8800"                 # Parse HEX
devtoolkit colorconv "rgb(255, 136, 0)"        # Parse RGB string
devtoolkit colorconv --rgb 255 136 0           # RGB values
devtoolkit colorconv --hex ff8800              # HEX without hash
devtoolkit colorconv --hsl 32 100 50           # HSL values
```

| Flag | Default | Description |
|------|---------|-------------|
| `COLOR` | — | Auto-detect format: HEX, rgb(...), hsl(...) |
| `--hex` | — | Input as HEX string |
| `--rgb R G B` | — | Input as RGB 0–255 |
| `--hsl H S L` | — | Input as HSL (H: 0–360, S/L: 0–100) |

### `sysinfo` — System Info

```bash
devtoolkit sysinfo                  # Show all info
devtoolkit sysinfo --python         # Python environment only
devtoolkit sysinfo --disk           # Disk usage only
devtoolkit sysinfo --json           # Output as JSON
```

| Flag | Default | Description |
|------|---------|-------------|
| `--python` | off | Show Python environment details only |
| `--disk` | off | Show disk usage only |
| `--json` | off | Output as JSON |

---

## ➕ How to Add a New Tool

Adding a new tool takes about 5 minutes:

1. **Create a new file** in `devtoolkit/tools/`, e.g. `devtoolkit/tools/mytools.py`

2. **Define a class** that inherits from `BaseTool`:

```python
# devtoolkit/tools/mytool.py
import argparse
from devtoolkit.core.plugin import BaseTool

class MyTool(BaseTool):
    name = "mytool"               # CLI subcommand: `devtoolkit mytool`
    description = "Does something awesome"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        # Add your argparse arguments here (optional)
        parser.add_argument("-n", "--name", default="world", help="Who to greet")

    def run(self, args: argparse.Namespace) -> None:
        # Your tool logic goes here
        print(f"Hello, {args.name}!")
```

3. **That's it.** Run `devtoolkit mytool` — DevToolkit auto-discovers the new tool.

> **Rules for a valid tool:**
> - Must inherit from `BaseTool`
> - Must define a non-empty `name` class attribute
> - Must implement the `run(self, args)` method

---

## 🗂 Project Structure

```
devtoolkit/
├── README.md
├── requirements.txt
├── pyproject.toml
├── devtoolkit/
│   ├── __init__.py
│   ├── main.py              # CLI entry point & auto-discovery engine
│   ├── core/
│   │   ├── __init__.py
│   │   └── plugin.py        # BaseTool abstract base class
│   └── tools/
│       ├── __init__.py
│       ├── timer.py         # Day 1: Pomodoro Timer
│       ├── weather.py       # Day 2: Weather Lookup
│       ├── passgen.py       # Day 3: Password Generator
│       ├── jsonfmt.py       # Day 4: JSON Formatter & Validator
│       ├── hashit.py        # Day 5: Hash Calculator
│       ├── uuidgen.py      # Day 6: UUID Generator
│       ├── base64tool.py   # Day 7: Base64 Encoder/Decoder
│       ├── epoch.py        # Day 8: Epoch Timestamp Converter
│       ├── note.py         # Day 9: Quick Note
│       ├── cronhelp.py     # Day 10: Cron Expression Helper
│       ├── baseconv.py     # Day 11: Base Converter
│       ├── wordcount.py   # Day 12: Word Count
│       ├── dice.py        # Day 13: Dice Roller
│       ├── lorem.py       # Day 14: Lorem Ipsum Generator
│       ├── rot13.py       # Day 15: ROT13 Cipher
│       ├── colorconv.py   # Day 16: Color Converter
│       └── sysinfo.py     # Day 17: System Info
└── .gitignore
```

---

## 🛣 Roadmap

| Day | Planned Tool | Description |
|-----|-------------|-------------|

---

## 🤝 Contributing

Contributions are welcome! To contribute a new tool:

1. Fork the repo
2. Create a branch: `git checkout -b day-N-toolname`
3. Add your tool to `devtoolkit/tools/`
4. Update the tool table in `README.md`
5. Open a pull request

---

## 📄 License

MIT License — feel free to use, modify, and share.
