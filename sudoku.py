from __future__ import annotations

from colorsys import hsv_to_rgb
from copy import deepcopy
from csv import reader
from pathlib import Path
from typing import Dict, List, Set, Tuple
from time import perf_counter
import logging

CONTAINER_TYPES = ("r", "c", "s")

def index_to_pos(t):
    return {"r": (r:=t//9), "c": (c:=t%9), "s": 3*(r//3) + c//3}

def row_column_to_index(r: int, c: int):
    return r*9+c

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

def reduce_options(fmtsol: _FormattedSolving, sudoku: Sudoku, n: int):
    if not sudoku.violated:
        if sudoku.done:
            return sudoku
        else:
            for kind in CONTAINER_TYPES:
                for kind_index in range(9):
                    if fmtsol._reduce_options(sudoku, kind, kind_index, n):
                        logging.info(f"{n} numbers in {n} tiles reduction")
                        return reduce_options(fmtsol,sudoku, 1)
            if n < 3:
                return reduce_options(fmtsol, sudoku, n+1)
            else:
                return cross_reduction(fmtsol, sudoku, 2)
    else:
        return False
    
def cross_reduction(fmtsol: _FormattedSolving, sudoku: Sudoku, scale: int):
    for direction in ("r", "c"):
        for option in range(1, 10):
            if fmtsol._n_by_n_removal(sudoku, scale, direction, option):
                logging.info(f"{option} appears in {scale}x{scale} square")
                return reduce_options(fmtsol, sudoku, 1)
    
    if scale < 3:
        return cross_reduction(fmtsol, sudoku, scale+1)
    else:
        return auto_try(fmtsol, sudoku)
        
def auto_try(fmtsol: _FormattedSolving, sudoku: Sudoku):
    for tile_index in range(81):
        tile = sudoku.tiles[tile_index]
        if tile.n_options == 2:
            logging.info(f"initiate bifurcation...")

            opts = deepcopy(tile.options)
            
            backup = deepcopy(sudoku)
            fmtsol.remove_options(backup, tile_index, {opts.pop()})
            if not (out:=reduce_options(fmtsol, backup, 1)):
                backup = deepcopy(sudoku)
                fmtsol.remove_options(backup, tile_index, {opts.pop()})
                out = reduce_options(fmtsol, backup, 1)

            logging.info(f"exit bifurcation")
            return out


def _format_tile(options: set, considered: set, affected: set) -> str:
    colorized = []
    for opt in options:
        if opt in considered:
            colorized.append(f"\033[92m{opt}\033[0m")
        elif opt in affected:
            colorized.append(f"\033[91m{opt}\033[0m")
        else:
            colorized.append(str(opt))
            
    joined = ", ".join(colorized)
    return f"[{joined}]"

def _print_grid(sudoku: Sudoku, considered_tiles: Set[int], considered_options: Set[int], affected_tiles: Set[int], affected_options: Set[int]):
    tiles = sudoku.tiles
    tile_width = (sudoku.max_options*3-2)+2
    square_width = (tile_width+1)*3-1
    row_strs = ""
    for row in range(9):
        col_strs = ""
        for col in range(9):
            tile_index = 9*row+col
            tile = tiles[tile_index]

            in_tile_considered = set() if not tile_index in considered_tiles else tile.options&considered_options
            in_tile_affected = set() if not tile_index in affected_tiles else tile.options&affected_options

            col_strs += f"{_format_tile(tile.options, in_tile_considered, in_tile_affected):<{tile_width}} "
            
            if (c:=col+1)%3==0 and c < 9:
                col_strs += "| "

        row_strs += f"{col_strs}\n"

        if (r:=row+1)%3==0 and r < 9:
            row_strs += f"={'=|='.join(square_width*'=')}="

def _print_no_output(sudoku: Sudoku, considered_tiles: Tuple[int], considered_options: Set[int], affected_tiles: Tuple[int], affected_options: Set[int]):
    pass


_FORMATTERS = {
    "grid": _print_grid,
    "empty": _print_no_output
}


class _Skipper:
    def __init__(self, formatting: str) -> None:
        self._fmt = _FORMATTERS[formatting]
        
    def __call__(self, *args):
        pass

class _Stepper(_Skipper):
    def __call__(self, sudoku: Sudoku, considered_tiles: Set[int], considered_options: Set[int], affected_tiles: Set[int], affected_options: Set[int]):
        self._fmt(sudoku, considered_tiles, considered_options, affected_tiles, affected_options)

        answering = True
        while answering:
            if not input("next step: (press ENTER)"):
                answering = False
            else:
                print("JUST HIT ENTER!")



_STEPPERS = {
    True: _Stepper,
    False: _Skipper
}

class _FormattedSolving:
    def __init__(self, formatting: str, stepping: False) -> None:
        self._stepper: _Stepper = _STEPPERS[stepping](formatting)

    def load_content(self, S: Sudoku, content: List[int]):
        occupied_tiles = []
        for tile_index in range(81):
            tile = S.tiles[tile_index]
            if val:=content[tile_index]:
                tile.options = {val}
                occupied_tiles.append((tile_index, val))

            S.tiles.append(tile)
            for kind in CONTAINER_TYPES:
                S.containers[kind][tile.pos[kind]].append(tile_index)

                counter = S.counters[kind][tile.pos[kind]]
                for o in tile.options:
                    counter[o-1].add(tile_index)

        for kind in CONTAINER_TYPES:
            for idx in range(9):
                self._reduce_options(S, kind, idx, 1)
        
        return S

    def _update_counter(self, S: Sudoku, tile_index: int, remove_options: set):
        # print("update counter")
        tile = S.tiles[tile_index]
        for kind in CONTAINER_TYPES:
            counter = S.counters[kind][tile.pos[kind]]
            for o in remove_options:
                where_option_is_found = counter[o-1]
                where_option_is_found -= {tile_index}

                if len(where_option_is_found) == 1:
                    where_only_one_left = list(where_option_is_found)[0]
                    remove_opts = deepcopy(S.tiles[where_only_one_left].options)-{o}

                    self._stepper(S, {where_only_one_left}, {o}, {where_only_one_left}, remove_options)

                    self.remove_options(S, where_only_one_left, remove_opts )

    def remove_options(self, S: Sudoku, where: int, which: set) -> bool:
        tile = S.tiles[where]
        # print(f"remove options {which} from tileopts {tile.options}")
        if (diff:=tile.options & which):
            # print(f"from tile r{tile.pos['r']}, c{tile.pos['c']} with opts {tile.options} remove {which}")
            tile.options -= which
            if tile.n_options > 0:
                self._update_counter(S, where, diff)
                return True
            else:
                # print(f"removed all options at r{tile.pos['r']}, c{tile.pos['c']}")
                S.violated = True
                return False
        else:
            return False
    

    def add_options(self, where: int, which: set) -> None:
        """
        future method artificially construct specific situations; useful in 
        particular when testing solving rules
        """
        pass
                

    def _get_equivalent_tiles(self, S: Sudoku, where: Set[int], tile_index: int) -> Set[int]:
        """
        return indices of all tiles within `where` that have the same options 
        as the tile at `which` 
        (`which` is also included)
        """
        
        if (tile:=S.tiles[tile_index]).n_options == 1:
            # print(f"tile {tile_index} has only one option")
            return {tile_index}

        else:
            matches = set()
            for tile_index in where:
                if S.tiles[tile_index].options == tile.options:
                    matches.add(tile_index)
            # print(f"found {len(matches)} equiv tile anyways")
            return matches if len(matches)==tile.n_options else set()

    def _reduce_options(self, S: Sudoku, kind: str, container_index: int, n: int) -> bool:
        success = False
        container = S.containers[kind][container_index]
        
        for tile_index in container:
            if len(matches:=self._get_equivalent_tiles(S, container, tile_index)) == n:

                self._stepper(S, matches, S.tiles[tile_index].options, set(container)-matches, S.tiles[tile_index].options)

                for unmatched in set(container)-matches:
                    if self.remove_options(S, unmatched, S.tiles[tile_index].options):
                        # print(f"remove option {self.tiles[tile_index].options} from {unmatched}")
                        success = True

        return success

    
    def _find_n_by_n(self, S: Sudoku, n: int, primary_kind: str, option: int):
        primary_kind_tiles = []
        secondary_kind, = {"r", "c"}-{primary_kind}
        secondary_to_consider = []
        for counter in S.counters[primary_kind]:
            if len(tile_idxs:=counter[option-1]) == n:
                primary_kind_tiles.append(tile_idxs)
                secondary_pos = {S.tiles[idx].pos[secondary_kind] for idx in tile_idxs}
                secondary_to_consider.append(secondary_pos)
                if secondary_to_consider.count(secondary_pos) == n:
                    return [primary_kind_tiles[i] for i, scpos in enumerate(secondary_to_consider) if scpos==secondary_pos]

        return None
        
    def _n_by_n_removal(self, S: Sudoku, n: int, primary_kind: str, option: int):
        throw_away = set()
        secondary_kind, = {"r", "c"}-{primary_kind}
        if (primary_kind_tiles:=self._find_n_by_n(S, n, primary_kind, option)):
            found_tiles = {idx for idxs in primary_kind_tiles for idx in idxs}
            # print(f"trying {n} x {n} removal with option {option} considering {found_tiles}")
            for tidx in primary_kind_tiles[0]:
                tile = S.tiles[tidx]
                secondary_kind_counter = S.counters[secondary_kind][tile.pos[secondary_kind]]
                secondary_kind_tiles = secondary_kind_counter[option-1]
                throw_away |= (secondary_kind_tiles - found_tiles)
            
            if len(throw_away) > 0:

                self._stepper(S, found_tiles, {option}, throw_away, {option})

                for tidx in throw_away:
                    self.remove_options(S, tidx, {option})

                return True

            else:
                return None     



def solve(path: Path, formatting: str, stepping: bool) -> Sudoku:
    fmtsol = _FormattedSolving(formatting, stepping)

    with open(path) as csvfile:
        rows = reader(csvfile, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    sudoku = fmtsol.load_content(Sudoku(), content)

    return reduce_options(fmtsol, sudoku, 1)

def load(path: Path) -> Sudoku:
    with open(path) as csvfile:
        rows = reader(csvfile, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    return Sudoku(content)

def save(sudoku: Sudoku, dest: Path):
    pass

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    # s = load("evil3.csv")
    s = solve("evil3.csv", "grid", True)
    print(s)
    # t0 = perf_counter()
    # s = solve(s)
    # T = perf_counter()-t0
    # print(f"solved in {round(T,6)}s, yielding:\n{s}")