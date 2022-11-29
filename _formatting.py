from __future__ import annotations

from typing import Set
from sudoku import Sudoku

def _format_tile(options: set, considered: set, affected: set) -> str:
    colorized = []
    for opt in options:
        if opt in considered:
            colorized.append(f"\033[92m{opt}\033[39m")
        elif opt in affected:
            colorized.append(f"\033[91m{opt}\033[39m")
        else:
            colorized.append(str(opt))
            
    joined = ",".join(colorized)
    return f"[{joined}]"

def _print_grid(sudoku: Sudoku, considered_tiles: Set[int], considered_options: Set[int], affected_tiles: Set[int], affected_options: Set[int]):
    tiles = sudoku.tiles
    tile_width = sudoku.max_options*2+1
    square_width = tile_width*3
    row_strs = ""
    for row in range(9):
        col_strs = ""
        for col in range(9):
            tile_index = 9*row+col
            tile = tiles[tile_index]

            in_tile_considered = set() if not tile_index in considered_tiles else tile.options&considered_options
            in_tile_affected = set() if not tile_index in affected_tiles else tile.options&affected_options

            col_strs += f"{_format_tile(tile.options, in_tile_considered, in_tile_affected)}{(tile_width-tile.n_options*2-1)*' '}"
            
            if (c:=col+1)%3==0 and c < 9:
                col_strs += u"\033[1m \u2551 \033[0m"

        row_strs += f"{col_strs}\n"

        line_char = u"\u2550"
        cross_char = u"\u256c"

        if (r:=row+1)%3==0 and r < 9:
            row_strs += f"\033[1m{(line_char+cross_char+line_char).join([square_width*line_char]*3)}\033[0m\n"

    print(row_strs)


_FORMATTERS = {
    "grid": _print_grid
}


class _Skipper:
    def __init__(self, formatting: str) -> None:
        self._fmt = _FORMATTERS[formatting]
        
    def show_step(self, *args):
        pass

    def show(self, sudoku: Sudoku):
        self._fmt(sudoku, set(), set(), set(), set())

class _Stepper(_Skipper):
    considered_tiles = set()
    considered_options = set()
    affected_tiles = set()
    affected_options = set()
    _counter = 0
    solving_message: str

    def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        # if sudoku.violated:
        self._counter += 1
        # if self._counter >= 380 or list(affected_tiles)[0]==35:
            # print(f"step {self._counter}:")
            # print(f"counters around 35: \nrow: {sudoku.counters['r'][3]}\ncol: {sudoku.counters['c'][8]}\nsqu: {sudoku.counters['s'][5]}")
        print("\033[H\033[J", end="")
        print(f"solving step {self._counter}: {self.solving_message}")
        self._fmt(sudoku, self.considered_tiles, self.considered_options, affected_tiles, affected_options)
        print(f"status: {'violated' if sudoku.violated else 'ok'}")

        answering = True
        while answering:
            if not input("next step: (press ENTER)"):
                answering = False
            else:
                print("JUST HIT ENTER!")
    



STEPPERS = {
    True: _Stepper,
    False: _Skipper
}
