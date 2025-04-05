<h1 align="center">Hashiwokakero Solver</h1>
<p align="center" style="font-size:16px"><strong>A Hashiwokakero Solver using PySAT, DPLL, A* and Brute-force with friendly CLI tools for solving and doing benchmark</strong></p>
<p align="center">  
  <img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/palette/macchiato.png" width="400" />
</p>

<p align="center">
  <img alt="Stars" src="https://badgen.net/github/stars/yuran1811/hcmus-ai-foundations--hashiwokakero">
  <img alt="Forks" src="https://badgen.net/github/forks/yuran1811/hcmus-ai-foundations--hashiwokakero">
  <img alt="Issues" src="https://badgen.net/github/issues/yuran1811/hcmus-ai-foundations--hashiwokakero">
  <img alt="Commits" src="https://badgen.net/github/commits/yuran1811/hcmus-ai-foundations--hashiwokakero">
  <img alt="Code Size" src="https://img.shields.io/github/languages/code-size/yuran1811/hcmus-ai-foundations--hashiwokakero">
</p>

## Features

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
```
or
```bash
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
uv run src/benchmark.py -m -e
```

## Tech Stack

<img src="https://skill-icons-livid.vercel.app/icons?i=py,latex&gap=60" height="36" />

## Screenshots

<div style="display:flex;gap:12px;justify-content:center">
	<img src="./Report/imgs/benchmark-solving_time.png" style="width:45%;max-width:380px">
	<img src="./Report/imgs/benchmark-peak_memory.png" style="width:45%;max-width:380px">
</div>

## Guide

- Read project guide [here](./Source/md/guide.md)
