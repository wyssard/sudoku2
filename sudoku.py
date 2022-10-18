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
                
    # def _update_counter(self, tile_index: int, remove_options: set):
    #     tile = self.tiles[tile_index]
    #     for kind in self.containers:
    #         counter = getattr(self, f"{kind}_count")[getattr(tile, kind)]
    #         for o in remove_options:
    #             where_option_is_found = counter[o-1]
    #             where_option_is_found.remove(tile_index)
    #             if len(where_option_is_found) == 1:
    #                 self.tiles[list(where_option_is_found)[0]].options = set([o])
    #                 counter[o-1] = set()
    #                 print("clean-up")

    def _update_counter(self, tile_index: int, remove_options: set):
        tile = self.tiles[tile_index]
        for kind in self.containers:
            counter = getattr(self, f"{kind}_count")[getattr(tile, kind)]
            for o in remove_options:
                where_option_is_found = counter[o-1]
                where_option_is_found -= set([tile_index])

    def _clear_superfluous(self) -> bool:
        success = False
        for kind in self.containers:
            counters = getattr(self, f"{kind}_count")
            for counter in counters:
                for n, tiles in enumerate(counter):
                    if len(tiles)==1:
                        tile = self.tiles[list(tiles)[0]]
                        diff = tile.options - set([n+1])
                        self._update_counter(list(tiles)[0], diff)
                        tile.options = set([n+1])
                        counter[n] = set()
                        success = True
        
        return success
                


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


    def _cross_reduction_rc_finder(self, kind: str, option: int):
        counters = getattr(self, f"{kind}_count")
        doubles = []
        for counter in counters:
            if len(tiles:=counter[option-1]) == 2:
                doubles.append(tiles)
        
        return doubles


    def _cross_reduction(self, kind: str, option: int):
        alt_kind = ["r", "c"]
        alt_kind.remove(kind)
        alt_kind = alt_kind[0]
        if (doubles:=self._cross_reduction_rc_finder(kind, option)):
            for tiles in doubles:
                alt_kind_indices = [getattr(self.tiles[index], alt_kind) for index in tiles]
                # print(f"double occurance of {option} in {kind} {getattr(self.tiles[list(tiles)[0]], kind)+1} at {tiles} in {alt_kind} {alt_kind_indices}")
                alt_counter = getattr(self, f"{alt_kind}_count")
                second_tiles = set()
                for i in (0,1):
                    if len(app_tiles:=alt_counter[alt_kind_indices[i]][option-1]) == 2:
                        second_tiles.add(list(app_tiles-tiles)[0])
                
                # print(f"second tiles {second_tiles}")
                if not len(second_tiles) == 2:
                    continue

                second_tiles_kind_index = [getattr(self.tiles[index], kind) for index in second_tiles]
                if (scidx:=second_tiles_kind_index[0]) == second_tiles_kind_index[1]:
                    if len(all_tiles:=getattr(self, f"{kind}_count")[scidx][option-1]) == 3:
                        outer_tile = list(all_tiles-second_tiles)[0]
                        self._remove_options(outer_tile, set([option]))
                        return True
                    

        else:
            return False

    def _return_options(self) -> List[int]:
        all =  [t.options for t in self.tiles]
        return [all[9*r:9*(r+1)] for r in range(9)]

    def _format(self, optionslist):
        return "\n".join(["| ".join(f"{str(e):<{2*(self.max_options+1)+self.max_options-1}}" for e in row) for row in optionslist])

    def __str__(self):
        return self._format(self._return_options())

    def solve(self, n) -> List[int]:
        # self._clear_superfluous()

        if self.max_options == 1:
            return self._return_options()

        # elif n > self.max_options:
        elif self.emergency_count == 2:
            print("couldn't solve")
            return self._return_specific_only(self._fewest_option())

        elif self.emergency_count == 1:
            self.emergency_count = 2
            for o in range(1, 10):
                for kind in ("r", "c"):
                    if self._cross_reduction(kind, o):
                        print("cross-reduction")
                        self.emergency_count = 0

            self.solve(1)
        
        elif n > self.max_options:
            self.emergency_count = 1
            if self._clear_superfluous():
                print("clean-up")
                self.emergency_count = 0

            self.solve(1)

        # elif n > self.max_options:
        #     self.emergency_count = 1
        #     for o in range(1, 10):
        #         for kind in ("r", "c"):
        #             if self._cross_reduction(kind, o):
        #                 self.emergency_count = 0
                
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
    s = load("hard.csv")
    # (s._format(solve(s)))
    solve(s)
    print(s)
    print(s.c_count[5])
    print(s.validate())