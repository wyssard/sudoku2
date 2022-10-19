from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Set, Tuple
from csv import reader
from colorsys import hsv_to_rgb

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


class Sudoku:
    kinds = ("r", "c", "s")
    max_options = 9
    emergency_count = 0

    def __init__(self, content: Tuple[int]) -> None:
        self.tiles: List[Tile] = []
        self.containers: Dict[str, List[List[int]]] = {}
        self.counters: Dict[str, List[List[Set[int]]]] = {}
        for kind in self.kinds:
            self.containers[kind] = [[] for _ in range(9)]
            self.counters[kind] = [[set() for _ in range(9)] for _ in range(9)]

        for tile_index in range(81):
            tile = Tile(**index_to_pos(tile_index))
            if val:=content[tile_index]:
                tile.options = set([val])

            self.tiles.append(tile)
            for kind in self.kinds:
                self.containers[kind][tile.pos[kind]].append(tile_index)

                counter = self.counters[kind][tile.pos[kind]]
                for o in tile.options:
                    counter[o-1].add(tile_index)
    
    def _update_counter(self, tile_index: int, remove_options: set):
        tile = self.tiles[tile_index]
        for kind in self.kinds:
            counter = self.counters[kind][tile.pos[kind]]
            for o in remove_options:
                where_option_is_found = counter[o-1]
                where_option_is_found -= set([tile_index])

    def _clear_superfluous(self) -> bool:
        success = False
        for kind in self.kinds:
            counters = self.counters[kind]
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
            for kind in self.kinds:
                container = self.containers[kind][tile.pos[kind]]
                matches = self._match_tiles(container, tile)
                if len(matches) == n:
                    for unmatched in set(container)-matches:
                        if self._remove_options(unmatched, tile.options):
                            success = True
                        
        return success

    def _cross_reduction_rc_finder(self, kind: str, option: int):
        doubles = []
        for counter in self.counters[kind]:
            if len(tiles:=counter[option-1]) == 2:
                doubles.append(tiles)
        
        return doubles

    def _cross_reduction(self, kind: str, option: int):
        alt_kind = ["r", "c"]
        alt_kind.remove(kind)
        alt_kind = alt_kind[0]
        if (doubles:=self._cross_reduction_rc_finder(kind, option)):
            for tiles in doubles:
                alt_kind_indices = [self.tiles[index].pos[alt_kind] for index in tiles]
                # print(f"double occurance of {option} in {kind} {getattr(self.tiles[list(tiles)[0]], kind)+1} at {tiles} in {alt_kind} {alt_kind_indices}")
                alt_counter = self.counters[alt_kind]
                second_tiles = set()
                for i in (0,1):
                    if len(app_tiles:=alt_counter[alt_kind_indices[i]][option-1]) == 2:
                        second_tiles.add(list(app_tiles-tiles)[0])
                
                # print(f"second tiles {second_tiles}")
                if not len(second_tiles) == 2:
                    continue

                second_tiles_kind_index = [self.tiles[index].pos[kind] for index in second_tiles]
                if (scidx:=second_tiles_kind_index[0]) == second_tiles_kind_index[1]:
                    if len(all_tiles:=self.counters[kind][scidx][option-1]) == 3:
                        outer_tile = list(all_tiles-second_tiles)[0]
                        self._remove_options(outer_tile, set([option]))
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


    def solve(self, n):
        if self.max_options == 1:
            return self

        elif self.emergency_count == 2:
            print("couldn't solve")
            return self

        elif self.emergency_count == 1:
            self.emergency_count = 2
            for o in range(1, 10):
                for kind in ("r", "c"):
                    if self._cross_reduction(kind, o):
                        print("cross-reduction")
                        self.emergency_count = 0

            return self.solve(1)
        
        elif n > self.max_options:
            self.emergency_count = 1
            if self._clear_superfluous():
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

    def validate(self) -> bool:
        goal = set(range(1,10))
        for kind in self.kinds:
            for container in self.containers[kind]:
                options = set()
                for tile_index in container:
                    options |= self.tiles[tile_index].options
                
                if not options == goal:
                    return False
        
        return True


    def _return_specific_only(self, which: int):    
        return [[tile if which in tile.options else None for tile in row] for row in self._return_options()]

    def print_specific_only(self, n):
        # doesn't work and I don't know why
        print(self._format(self._return_specific_only(n), True))

    def _format(self, tile_rows: List[List[Tile]], colorize=False):
        colors = [";".join([str(int(c*256)) for c in hsv_to_rgb(h/9, 1, 1)]) for h in range(9)]
        width = 2*(self.max_options+1)+self.max_options-1
        base_str = lambda tile: f"{str(tile.options):<{width}}"
        if colorize:
            color_str = lambda tile: f"\033[38;2;{colors[tile.pos['s']]}m{base_str(tile)}\033[0m"
        else:
            color_str = base_str

        return "\n".join([" ".join(color_str(tile) for tile in row) for row in tile_rows])
    
    def __str__(self):
        return self._format(self._return_options(), True)


  
def solve(sudoku: Sudoku) -> Sudoku:
    return sudoku.solve(1)

def load(path: Path) -> Sudoku:
    with open(path) as csvfile:
        rows = reader(csvfile, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    return Sudoku(content)

def save(sudoku: Sudoku, dest: Path):
    pass

if __name__=="__main__":
    s = load("evil.csv")
    print(solve(s), "\n")
    # s.print_specific_only(3)
    print(s.counters["c"][5])
    print(s.validate())