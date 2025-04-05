from argparse import ArgumentParser


def with_version_arg(parser: ArgumentParser):
    parser.add_argument("-v", "--version", help="Version", action="store_true")


def with_algo(parser: ArgumentParser):
    parser.add_argument(
        "-a",
        "--algo",
        help="Choose which algo will be used",
        choices=["pysat", "astar", "backtrack", "brute"],
    )


def with_input_path(parser: ArgumentParser):
    parser.add_argument(
        "-i",
        "--input",
        help="Path to the input file",
        default="./data/input/7x7/input-01.txt",
    )


def with_export_output(parser: ArgumentParser):
    parser.add_argument(
        "-e",
        "--export",
        help="Export result to output",
        action="store_true",
    )


def with_metrics(parser: ArgumentParser):
    parser.add_argument(
        "-m",
        "--metrics",
        help="Export metrics images",
        action="store_true",
    )


def parse_args(*, prog: str, desc: str, wrappers: list):
    parser = ArgumentParser(
        prog=prog,
        description=desc,
    )

    for wrapper in wrappers:
        wrapper(parser)

    return parser.parse_args()
