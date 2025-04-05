def time_convert(time: float) -> str:
    if time < 1:
        return f"{time * 1000:.2f} ms"
    return f"{time:.2f} s"


def byte_convert(num: float) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num < 1024:
            return f"{num:.2f} {unit}"
        num /= 1024.0

    return f"{num:.2f} PB"


def prettify_output(output: list[list[str]]):
    if output:
        [print(" ".join(x)) for x in output]
