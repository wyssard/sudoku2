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


    def _reduce_one(self, tile: Tile) -> bool:
        success = False
        
        if tile.n_options == 1:
            for kind in self.containers:
                container = getattr(self, kind)[getattr(tile, kind)]
                for tile_index in container:
                    c_tile = self.tiles[tile_index]
                    if tile.options.issubset(c_tile.options) and c_tile.n_options > 1:
                        print(f"remove {tile.options} at ({tile.r}, {tile.c}) from {c_tile.options}")
                        c_tile.options -= tile.options
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

    def _cleanup_reduction(self, container: List[int]) -> bool:
        success = False
        nums = [[] for _ in range(9)]

        for tile_index in container:
            tile = self.tiles[tile_index]
            for o in tile.options:
                nums[o-1].append(tile_index)
        
        # print("\n".join(f"{n+1}: {len(v)}" for n,v in enumerate(nums)))
        for n, tile_indices in enumerate(nums):
            if len(tile_indices) == 1:
                t_tile = self.tiles[tile_indices[-1]]
                if len(t_tile.options) > 1:
                    t_tile.options = set([n+1])
                # print(f"tile {tile_indices[-1]} is the only one in container with option {n+1}")

                    success = True

        return success


    def _return_options(self) -> List[int]:
        all =  [t.options for t in self.tiles]
        return [all[9*r:9*(r+1)] for r in range(9)]


    def _format(self, optionslist):
        return "\n".join(["| ".join(f"{str(e):<{2*(self.max_options+1)+self.max_options-1}}" for e in row) for row in optionslist])


    def __str__(self):
        return self._format(self._return_options())

    def solve(self, n) -> List[int]:
        if self.max_options == 1:
            return self._return_options()

        elif self.emergency_count > 0:
            print("couldn't solve")
            return self._return_specific_only(self._fewest_option())
        
        elif n > self.max_options:
            self.emergency_count = 1
            for kind in self.containers:
                for i in range(9):
                    container = getattr(self, kind)[i]
                    if self._cleanup_reduction(container):
                        print("clean-up")
                        self.emergency_count = 0
                
            return self.solve(1)

        else:
            n_success = 0
            self.max_options = 0
            for tile_index in range(81):
                tile = self.tiles[tile_index]
                if self._reduce_options(tile, n):
                    n_success += 1
                    print(f"n = {n} reduction")
                
                self.max_options = max(self.max_options, tile.n_options)

            if n_success > 0:
                return self.solve(1)
            else:
                return self.solve(n+1)

    def _fewest_option(self):
        appearances = [0]*9
        for tile in self.tiles:
            for o in tile.options:
                appearances[o-1] += 1
        
        return appearances.index(min(appearances))+1

    def validate(self) -> bool:
        goal = set(range(1,10))
        for kind in self.containers:
            for container in getattr(self, kind):
                options = set()
                for tile_index in container:
                    options |= self.tiles[tile_index].options
                
                if not options == goal:
                    return False
        
        return True


    def _tow_three_rule(self, container: List[int], search_in: str, n: int):
        pass


    def _return_specific_only(self, which: int):        
        return [[opts if which in opts else None for opts in row] for row in self._return_options()]

    def print_specific_only(self):
        print(self._format(self._return_specific_only(self._fewest_option())))

  
def solve(sudoku: Sudoku) -> List[int]:
    return sudoku.solve(1)

def load(path: Path) -> Sudoku:
    with open(path) as csvfile:
        rows = reader(csvfile, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    return Sudoku(content)



if __name__=="__main__":
    s = load("evil.csv")
    print(s._format(solve(s)))

    print(s.validate())