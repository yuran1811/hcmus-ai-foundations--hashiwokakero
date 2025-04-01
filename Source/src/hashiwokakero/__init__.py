from solvers import (
    solve_with_astar,
    solve_with_backtracking,
    solve_with_bruteforce,
    solve_with_pysat,
)
from utils import (
    encode_pbequal,
    get_input_path,
    get_project_toml_data,
    parse_args,
    parse_input,
    prettify_output,
    with_algo,
    with_input_path,
    with_version_arg,
)


def dev():
    from pysat.solvers import Glucose42

    literals = [1, 2, 3, 4]
    weights = [1, 2, 3, 4]
    k = 5

    max_var = literals[-1]
    clauses = encode_pbequal(literals, weights, k, max_var)

    with Glucose42(bootstrap_with=clauses) as solver:
        if solver.solve():
            model = solver.get_model()
            print("Solution found:", model[:max_var] if model else [])
        else:
            print("No solution exists")


def solve(solver, file_path: str = get_input_path(7, 1)):
    try:
        prettify_output(solver(parse_input(file_path)))
    except Exception as _:
        print(f"[error]::{_}")


def main() -> int:
    __toml = get_project_toml_data()
    args = parse_args(
        prog=__toml["name"],
        desc=__toml["description"],
        wrappers=[with_version_arg, with_algo, with_input_path],
    )

    if args.version:
        print(
            f"{__toml['name']} {__toml['version']} -- by {', '.join([x['name'] for x in __toml['authors']])} -- {__toml['license']['text']} LICENSE"
        )
        return 0

    match args.algo:
        case "pysat":
            solve(solve_with_pysat, args.input)
        case "astar":
            solve(solve_with_astar, args.input)
        case "backtrack":
            solve(solve_with_backtracking, args.input)
        case "brute":
            solve(solve_with_bruteforce, args.input)

    return 0
