from solvers import (
    solve_with_astar,
    solve_with_backtracking,
    solve_with_bruteforce,
    solve_with_pysat,
)
from utils import (
    encode_hashi,
    extract_solution,
    generate_output,
    get_input_path,
    get_project_toml_data,
    parse_args,
    parse_input,
    prettify_output,
    validate_solution,
    with_algo,
    with_input_path,
    with_version_arg,
)


def dev():
    from pysat.solvers import Glucose42

    grid = parse_input(get_input_path(20, 4))
    cnf, edge_vars, islands, _ = encode_hashi(
        grid, use_pysat=True, use_self_pbenc=False
    )
    print(len(cnf.clauses))
    # print("\n", cnf.clauses, "\n")

    with Glucose42(bootstrap_with=cnf) as solver:
        while solver.solve():
            model = solver.get_model()
            num_clauses = solver.nof_clauses()
            if not model or (num_clauses and num_clauses > len(cnf.clauses)):
                break

            # print(model[: len(edge_vars) * 2])

            if validate_solution(islands, edge_vars, model):
                prettify_output(
                    generate_output(grid, islands, extract_solution(model, edge_vars))
                )
                return

            solver.add_clause([-x for x in model])


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
