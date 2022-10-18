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
            setattr(self, kind, [[] for _ in range(9)])
            setattr(self, f"{kind}_count", [[set() for _ in range(9)] for _ in range(9)])

        for tile_index in range(81):
            tile = Tile(*get_rcs_index(tile_index))
            if val:=content[tile_index]:
                tile.options = set([val])

            self.tiles.append(tile)
            for kind in self.containers:
                getattr(self, kind)[getattr(tile, kind)].append(tile_index)
                counter = getattr(self, f"{kind}_count")[getattr(tile, kind)]
                for o in tile.options:
                    counter[o-1].add(tile_index)
                
    def _update_counter(self, tile_index: int, remove_options: set):
        tile = self.tiles[tile_index]
        for kind in self.containers:
            counter = getattr(self, f"{kind}_count")[getattr(tile, kind)]
            for o in remove_options:
                where_option_is_found = counter[o-1]
                where_option_is_found.remove(tile_index)
                if len(where_option_is_found) == 1:
                    self.tiles[list(where_option_is_found)[0]].options = set([o])

    def _match_tiles(self, where: List[int], which: Tile) -> Set[int]:
        matches = set()
        for tile_index in where:
            if self.tiles[tile_index].options == which.options:
                matches.add(tile_index)
        
        return matches

    def _remove_options(self, where: int, which: set) -> bool:
        tile = self.tiles[where]
        if (diff:=tile.options & which):
            tile.options -= which
            self._update_counter(where, diff)
            return True
        else:
            return False

    # def _reduce_one(self, tile: Tile) -> bool:
    #     success = False
        
    #     if tile.n_options == 1:
    #         for kind in self.containers:
    #             container = getattr(self, kind)[getattr(tile, kind)]
    #             for tile_index in container:
    #                 c_tile = self.tiles[tile_index]
    #                 if tile.options.issubset(c_tile.options) and c_tile.n_options > 1:
    #                     print(f"remove {tile.options} at ({tile.r}, {tile.c}) from {c_tile.options}")
    #                     c_tile.options -= tile.options
    #                     success = True

    #     return success

    def _reduce_options(self, tile: Tile, n: int) -> bool:
        success = False
        if tile.n_options == n:
            for kind in self.containers:
                container = getattr(self, kind)[getattr(tile, kind)]
                matches = self._match_tiles(container, tile)
                if len(matches) == n:
                    for unmatched in set(container)-matches:
                        if self._remove_options(unmatched, tile.options):
                            success = True
                        
        return success

    # def _cleanup_superfluous(self):
    #     success = False
    #     for kind in self.containers:
    #         counters = getattr(self, f"{kind}_count")
    #         for kind_counter in counters:

    #         for n, tile_indices in enumerate(counter):
    #             if len(tile_indices) == 1:
    #                 tile_index = tile_indices[-1]
    #                 tile = self.tiles[tile_index]
    #                 if len(tile.options) > 1:
    #                     if self._remove_options(tile_index, tile.options - set([n+1])):
    #                         success = True
                        
    #     return success
                        

    # def _cleanup_reduction(self, container: List[int]) -> bool:
    #     success = False
    #     nums = [[] for _ in range(9)]

    #     for tile_index in container:
    #         tile = self.tiles[tile_index]
    #         for o in tile.options:
    #             nums[o-1].append(tile_index)
        
    #     # print("\n".join(f"{n+1}: {len(v)}" for n,v in enumerate(nums)))
    #     for n, tile_indices in enumerate(nums):
    #         if len(tile_indices) == 1:
    #             t_tile = self.tiles[tile_indices[-1]]
    #             if len(t_tile.options) > 1:
    #                 t_tile.options = set([n+1])
    #             # print(f"tile {tile_indices[-1]} is the only one in container with option {n+1}")

    #                 success = True

    #     return success

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

        elif n > self.max_options:
        # elif self.emergency_count > 0:
            print("couldn't solve")
            return self._return_specific_only(self._fewest_option())
        
        # elif n > self.max_options:
        #     self.emergency_count = 1
        #     if self._cleanup_superfluous():
        #         print("clean-up")
        #         self.emergency_count = 0
                
        #     return self.solve(1)

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

    # def _two_tree_next_to_check(self, container: List[int], option: int) -> list:
    #     check_next = []
    #     for tile_index in container:
    #         c_tile = self.tiles[tile_index]
    #         if (c_tile.n_options > 1) and (option in c_tile.options):
    #             check_next.append(c_tile)

    #     return check_next



    # def _two_three_base(self, tile: Tile, option: int) -> bool:
    #     directions = ("r", "c")
    #     if (tile.n_options > 1) and (option in tile.options):
    #         for direction, alt_direction in (("r", "c"), ("c", "r")):
    #             container = getattr(self, direction)[getattr(tile, direction)]
    #             check_next = []
    #             for tile_index in container:
    #                 c_tile = self.tiles[tile_index]
    #                 if (c_tile.n_options > 1) and (option in c_tile.options):
    #                     check_next.append(c_tile)

    #             if len(check_next) == 2:
    #                 for n_tile in check_next:
    #                     container = getattr(self, alt_direction)[getattr(n_tile, alt_direction)]


                
        
    #     else:
    #         return False
                    


    # def _tow_three_rule(self, tile: Tile) -> bool:
    #     pass

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
    print(s)
    print(s.s_count[8])
    print(s.validate())