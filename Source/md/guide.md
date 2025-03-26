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
pip install -r requirements.txt
```

**Running the Project**

```bash
uv run dev
```

**Testing**

```bash
uv run pytest
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
