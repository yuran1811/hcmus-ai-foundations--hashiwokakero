from pysat.card import EncType as CardEncType
from pysat.pb import EncType as PBEncType

from __types import Grid

from .base import encode_hashi
from .data import parse_input


class CNFGenerator:
    def __init__(self) -> None:
        self.grid: Grid = []

    def parse_from_file(self, file_path: str):
        self.grid = parse_input(file_path)

    def generate(
        self,
        grid: Grid,
        pbenc: int = PBEncType.bdd,
        cardenc: int = CardEncType.mtotalizer,
        *,
        use_pysat: bool = False,
    ):
        return encode_hashi(grid, pbenc, cardenc, use_pysat=use_pysat)
