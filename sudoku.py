from __future__ import annotations

from colorsys import hsv_to_rgb
from typing import Dict, List, Set

CONTAINER_TYPES = ("r", "c", "s")

# To Do
# - reposition the 'solving launchers' into the solver class
# - consider some minor coloring issues in the stepper
# - rework stepping system; only invoke step if options are to be removed
#   by using the considered and affected tiles as class variables of the 
#   stepper classes [done]
# - analyse curious behavior of the _update_counter functions (which is removing
#   options that shouldn't be removed) [done]

def row_column_to_index(r: int, c: int):
    return r*9+c

def index_to_pos(t):
    return {"r": (r:=t//9), "c": (c:=t%9), "s": 3*(r//3) + c//3}

class Tile:
    def __init__(self, r: int, c: int, s: int) -> None:
        self.pos = {"r": r, "c": c, "s": s}
        self._options = set(range(1, 10))
        self.n_options = 9

    def __getitem__(self, key: str):
        return self.pos[key]

    @property
    def options(self) -> set:
        return self._options

    @options.setter
    def options(self, new_options) -> None:
        self._options = new_options
        self.n_options = len(new_options)

    @classmethod
    def to_none_tile(cls, tile: Tile) -> Tile:
        obj = super().__new__(cls)
        obj.pos = tile.pos
        obj._options = {}
        obj.n_options = 0
        return obj

class Sudoku:
    def __init__(self) -> None:
        self.violated = False

        self.tiles: List[Tile] = []
        self.containers: Dict[str, List[List[int]]] = {}
        self.counters: Dict[str, List[List[Set[int]]]] = {}

        for kind in CONTAINER_TYPES:
            self.containers[kind] = [[] for _ in range(9)]
            self.counters[kind] = [[set() for _ in range(9)] for _ in range(9)]

        for tile_index in range(81):
            self.tiles.append(Tile(**index_to_pos(tile_index)))


    @property
    def max_options(self) -> int:
        return max(tile.n_options for tile in self.tiles)

    @property
    def done(self) -> bool:
        return True if self.max_options==1 and not self.violated else False

    def is_valid(self) -> bool:
        if not self.violated:
            goal = set(range(1,10))
            for kind in CONTAINER_TYPES:
                for i in range(9):
                    container = self.containers[kind][i]
                    options = set()
                    for tile_index in container:
                        options |= self.tiles[tile_index].options
                    
                    if not options == goal:
                        print(f"error at {kind} {i}")
                        return False
            
            return True
        else:
            return False
    

    def _fewest_option(self):
        appearances = [0]*9
        for tile in self.tiles:
            for o in tile.options:
                appearances[o-1] += 1
        
        return appearances.index(min(appearances))+1


    def _return_options(self) -> List[List[Tile]]:
        return [self.tiles[9*r:9*(r+1)] for r in range(9)]

    def _return_specific_only(self, which: int):    
        return [[tile if which in tile.options else Tile.to_none_tile(tile) for tile in row] for row in self._return_options()]


    def _format(self, tile_rows: List[List[Tile]], colorize=False):
        colors = [";".join([str(int(c*256)) for c in hsv_to_rgb(h/9, 1, 1)]) for h in range(9)]
        width = 2*(self.max_options+1)+self.max_options-1
        base_str = lambda tile: f"{str(tile.options):<{width}}"
        if colorize:
            color_str = lambda tile: f"\033[38;2;{colors[tile.pos['s']]}m{base_str(tile)}\033[0m"
        else:
            color_str = base_str

        return "\n".join([" ".join(color_str(tile) for tile in row) for row in tile_rows])
    
    def print_specific(self, which: int):
        print(self._format(self._return_specific_only(which), True))

    def __str__(self):
        return self._format(self._return_options(), True)
