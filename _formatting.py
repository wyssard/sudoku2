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

def _get_row_delimiter(left, center, right, width, main):
    return f"{left}{main}{(main+center+main).join([(width)*main]*3)}{main}{right}\n"

def _print_grid(sudoku: Sudoku, considered_tiles: Set[int], considered_options: Set[int], affected_tiles: Set[int], affected_options: Set[int]):
    tiles = sudoku.tiles
    tile_width = sudoku.max_options*2+1
    square_width = tile_width*3
    row_strs = ""

    h_line_char = u"\u2500"
    v_line_char = u"\u2502"
    cross_char = u"\u253c"
    lu_angle = u"\u256d"
    ll_angle = u"\u2570"
    ru_angle = u"\u256e"
    rl_angle = u"\u256f"
    l_t = u"\u251c"
    r_t = u"\u2524"
    u_t = u"\u252c"
    d_t = u"\u2534"

    row_strs += _get_row_delimiter(lu_angle, u_t, ru_angle, square_width, h_line_char)

    for row in range(9):
        col_strs = f"{v_line_char} "
        for col in range(9):
            tile_index = 9*row+col
            tile = tiles[tile_index]

            in_tile_considered = set() if not tile_index in considered_tiles else tile.options&considered_options
            in_tile_affected = set() if not tile_index in affected_tiles else tile.options&affected_options

            col_strs += f"{_format_tile(tile.options, in_tile_considered, in_tile_affected)}{(tile_width-tile.n_options*2-1)*' '}"
            
            if (c:=col+1)%3==0 and c < 9:
                col_strs += f"\033[0m {v_line_char} \033[0m"

        row_strs += f"{col_strs} {v_line_char}\n"

        

        if (r:=row+1)%3==0 and r < 9:
            row_strs += _get_row_delimiter(l_t, cross_char, r_t, square_width, h_line_char)
            # row_strs += f"\033[0m{l_t}{h_line_char}{(h_line_char+cross_char+h_line_char).join([(square_width)*h_line_char]*3)}{h_line_char}{r_t}\033[0m\n"

    row_strs += _get_row_delimiter(ll_angle, d_t, rl_angle, square_width, h_line_char)

    print(row_strs)

_FORMATTERS = {
    "grid": _print_grid
}


class Skipper:
    def __init__(self, formatting: str) -> None:
        self._fmt = _FORMATTERS[formatting]
    
    def set_consideration(self, *args):
        pass

    def show_step(self, *args):
        pass

    def show(self, sudoku: Sudoku):
        self._fmt(sudoku, set(), set(), set(), set())

class Stepper(Skipper):
    considered_tiles = set()
    considered_options = set()
    affected_tiles = set()
    affected_options = set()
    _counter = 0
    solving_message: str

    def set_consideration(self, tiles: set, options: set, message: Stepper):
       self.considered_tiles = tiles
       self.considered_options = options
       self.solving_message = message

    def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        
        self._counter += 1
        
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
    True: Stepper,
    False: Skipper
}
