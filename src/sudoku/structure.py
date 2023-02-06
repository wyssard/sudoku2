from __future__ import annotations

from colorsys import hsv_to_rgb
from typing import Dict, List, Set

CONTAINER_TYPES = ("r", "c", "s")

def row_column_to_index(r: int, c: int):
    return r*9+c

def index_to_pos(t):
    return {"r": (r:=t//9), "c": (c:=t%9), "s": 3*(r//3) + c//3}

class Tile:
    def __init__(self, r: int, c: int, s: int) -> None:
        self.pos = {"r": r, "c": c, "s": s}
        self._options = set(range(1, 10))
        self.n_options = 9
        self.solved_at = 0

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
    def __init__(self, content: List[int]) -> None:
        self.violated = False

        self.tiles: List[Tile] = []
        self.containers: Dict[str, List[List[int]]] = {}
        self.occurrences: Dict[str, List[List[Set[int]]]] = {}

        for kind in CONTAINER_TYPES:
            self.occurrences[kind] = [[set() for _ in range(9)] for _ in range(9)]
            self.containers[kind] = [[] for _ in range(9)]

        given_tiles = []
        for tile_index in range(81):
            tile = Tile(**index_to_pos(tile_index))
            if val:=content[tile_index]:
                tile.options = {val}
                given_tiles.append(tile_index)

            for kind in CONTAINER_TYPES:
                self.containers[kind][tile.pos[kind]].append(tile_index)

                occurrence = self.occurrences[kind][tile.pos[kind]]
                for o in tile.options:
                    occurrence[o-1].add(tile_index)
                
            self.tiles.append(tile)

        for tile_index in given_tiles:
            tile = self.tiles[tile_index]

            # option 'o' has occurrence position 'o-1'
            option_occurrence_pos = list(tile.options)[0]-1

            for kind in CONTAINER_TYPES:
                occurrence = self.occurrences[kind][tile.pos[kind]]
                occurrence[option_occurrence_pos] = {tile_index}

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

    def get_tiles(self) -> List[List[Tile]]:
        return [[t for t in self.tiles[9*r:9*(r+1)]] for r in range(9)]

    def get_options(self) -> List[List[set]]:
        return [[t.options for t in self.tiles[9*r:9*(r+1)]] for r in range(9)]

    def get_solved(self) -> List[List[int]]:
        return [[list(tile.options)[0] for tile in row] for row in self.get_tiles()]
         
    def get_complexity_map(self) -> List[List[int]]:
        return [[tile.solved_at for tile in row] for row in self.get_tiles()]