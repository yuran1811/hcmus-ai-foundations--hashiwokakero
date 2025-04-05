# Installation

**Package Manager**

- This project using [uv](https://docs.astral.sh/uv/) as package manager.

# Development

**Install dependencies**

```bash
uv sync
```

or

```bash
uv add -r requirements.txt
```

**Unit Testing**

```bash
uv run pytest
```

**Run Solver**

```bash
usage: hashiwokakero [-h] [-v] [-a {pysat,astar,backtrack,brute}] [-i INPUT]

HCMUS AI Foundations -- Hashiwokakero Project

options:
  -h, --help            show this help message and exit
  -v, --version         Version
  -a {pysat,astar,backtrack,brute}, --algo {pysat,astar,backtrack,brute}
                        Choose which algo will be used
  -i INPUT, --input INPUT
                        Path to the input file
```

```bash
uv run main -a pysat -i "./data/input/20x20/input-04.txt"
# or
uv run main -a astar -i "./data/input/13x13/input-05.txt"
```

**Run Benchmark**

```bash
usage: hashiwokakero [-h] [-m] [-e]

HCMUS AI Foundations -- Hashiwokakero Project

options:
  -h, --help     show this help message and exit
  -m, --metrics  Export metrics images
  -e, --export   Export result to output
```

```bash
uv run src/benchmark.py
```

or

```bash
uv run src/benchmark.py -e -m
```

**Lint**

```bash
uvx ruff check
```

**Format**

```bash
uvx ruff format
```

**Generate `requirements.txt`**

```bash
uv pip compile pyproject.toml -o requirements.txt
```
