from __future__ import annotations
from copy import deepcopy
from pathlib import Path
from typing import List, Set, Tuple
from csv import reader

def get_rcs_index(t):
    return [(r:=t//9), (c:=t%9), 3*(r//3) + c//3]

class Tile:
    def __init__(self, row, column, square) -> None:
        self.r = row
        self.c = column
        self.s = square
        self._options = set(range(1, 10))
        self.n_options = 9

    @property
    def options(self) -> set:
        return self._options

    @options.setter
    def options(self, new_options) -> None:
        self._options = new_options
        self.n_options = len(new_options)

class Sudoku:
    containers = ("r", "c", "s")
    max_options = 9
    emergency_count = 0

    def __init__(self, content: Tuple[int]) -> None:
        self.tiles: List[Tile] = []
        for kind in self.containers:
            setattr(self, kind, self._empty_grid())

        for tile_index in range(81):
            tile = Tile(*get_rcs_index(tile_index))
            if val:=content[tile_index]:
                tile.options = set([val])

            self.tiles.append(tile)
            for kind in self.containers:
                getattr(self, kind)[getattr(tile, kind)].append(tile_index)


    @staticmethod
    def _empty_grid():
        return [[] for _ in range(9)]


    def _match_tiles(self, where: List[int], which: Tile) -> Set[int]:
        matches = set()
        for tile_index in where:
            if self.tiles[tile_index].options == which.options:
                matches.add(tile_index)
        
        return matches

    def _remove_options(self, where: set, which: set) -> bool:
        success = False
        for tile_index in where:
            tile = self.tiles[tile_index]
            if not tile.options.isdisjoint(which):
                tile.options -= which
                success = True

        return success


    def _reduce_options(self, tile: Tile, n: int) -> bool:
        success = False
        if tile.n_options == n:
            for kind in self.containers:
                container = getattr(self, kind)[getattr(tile, kind)]
                matches = self._match_tiles(container, tile)
                if len(matches) == n:
                    if self._remove_options(set(container)-matches, tile.options):
                        success = True
                        
        return success


    def _extract_singles(self, tile: Tile) -> bool:
        # THIS METHODS IS STRAIGHT UP WRONG

        match = None
        for kind in self.containers:
            container = getattr(self, kind)[getattr(tile, kind)]
            for tile_index in container:
                c_tile = self.tiles[tile_index]
                if tile.n_options == c_tile.n_options-1:
                    if tile.options.issubset(c_tile.options):
                        if not match:
                            match = c_tile
                        else:
                            break

        if match:
            print(f"found options {match.options}, remove options {tile.options}")
            match.options = match.options - tile.options
            print(f"it remains {match.options}")
            return True
        else:
            return False


    def _return_as_list(self) -> List[int]:
        return [t.options for t in self.tiles]


    def solve(self, n) -> List[int]:
        if self.max_options == 1:
            return self._return_as_list()
        
        elif n > self.max_options:
            self.emergency_count += 1
            self.max_options = 0
            for tile_index in range(81):
                tile = self.tiles[tile_index]
                
                self._extract_singles(tile)

                self.max_options = max(self.max_options, tile.n_options)

            return self.solve(1)
        
        elif self.emergency_count > 1:
            print("couldnt solve")
            # print([t.n_options for t in self.tiles])
            # return self._return_as_list()
            print("len check:")
            for t in range(81):
                tile = self.tiles[t]
                if not len(tile.options) == tile.n_options:
                    print("len issue discovered")

            print("opitons:")
            return self._return_as_list()

        else:
            n_success = 0
            self.max_options = 0
            for tile_index in range(81):
                tile = self.tiles[tile_index]
                if self._reduce_options(tile, n):
                    n_success += 1
                
                self.max_options = max(self.max_options, tile.n_options)

            if n_success > 0:
                return self.solve(1)
            else:
                return self.solve(n+1)
  
def solve(sudoku: Sudoku) -> List[int]:
    return sudoku.solve(1)

def load(path: Path) -> Sudoku:
    with open(path) as csvfile:
        rows = reader(csvfile, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    return Sudoku(content)


if __name__=="__main__":
    print(solve(load("example.csv")))