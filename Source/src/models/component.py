from dataclasses import dataclass


@dataclass
class Island:
    x: int  # Row index
    y: int  # Column index
    num: int  # Required bridges


@dataclass
class Bridge:
    start: Island
    end: Island
    direction: str  # 'horizontal' or 'vertical'
    count: int = 0  # 0, 1, or 2
