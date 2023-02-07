"""
Example module to illustrate a coupling of the solver to the console as 
frontend. Therefore, a corresponding `Trigger` and `Formatter` class must be
implemented.
"""

from __future__ import annotations

from typing import Set, Dict, Type

from .structure import Sudoku
from .stepping import StepTrigger, StepperBase, AnyStep, Skipper, InterestingStep
from .formatting import BlankFormatter
from .solvertools import generate_solver
from .solvingmethods import FmtSolvingMethod, ScaledXWing, Bifurcation

class ConsoleTrigger(StepTrigger):
    """
    Trigger that requires the user to press 'enter' to show the next solving
    step.
    """
    def trigger_next_step(self) -> None:
        answering = True
        while answering:
            if not input("next step: (press ENTER)"):
                answering = False
            else:
                print("JUST HIT ENTER!")

class ConsoleFormatter(BlankFormatter):
    """
    Basic formatter to print the solutions steps, i.e. the partially solved
    puzzle, to the console. Use the `flush` attribute to decide whether the 
    solution steps are stringed together in the console or if the previous step
    is consecutively removed. 
    """
    def __init__(self, render_message=True, flush=False) -> None:
        self.flush = flush
        self.r_msg = render_message
    
    def _format_tile(self, options: set, considered: set, affected: set) -> str:
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

    def _get_row_delimiter(self, left, center, right, width, main):
        return f"{left}{main}{(main+center+main).join([(width)*main]*3)}{main}{right}\n"

    def _prepare_string(self, sudoku: Sudoku, considered_tiles: Set[int], considered_options: Set[int], affected_tiles: Set[int], affected_options: Set[int]):
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

        row_strs += self._get_row_delimiter(lu_angle, u_t, ru_angle, square_width, h_line_char)

        for row in range(9):
            col_strs = f"{v_line_char} "
            for col in range(9):
                tile_index = 9*row+col
                tile = tiles[tile_index]

                in_tile_considered = set() if not tile_index in considered_tiles else tile.options&considered_options
                in_tile_affected = set() if not tile_index in affected_tiles else tile.options&affected_options

                col_strs += f"{self._format_tile(tile.options, in_tile_considered, in_tile_affected)}{(tile_width-tile.n_options*2-1)*' '}"
                
                if (c:=col+1)%3==0 and c < 9:
                    col_strs += f" {v_line_char} "

            row_strs += f"{col_strs} {v_line_char}\n"

            if (r:=row+1)%3==0 and r < 9:
                row_strs += self._get_row_delimiter(l_t, cross_char, r_t, square_width, h_line_char)

        row_strs += self._get_row_delimiter(ll_angle, d_t, rl_angle, square_width, h_line_char)
        return row_strs

    def render(self, sudoku: Sudoku, considered_tiles: set, considered_options: set, affected_tiles: set, affected_options: set, solving_step: int, solving_message: str):
        if self.flush:
            print("\033[H\033[J", end="")
            
        print(f"solving step {solving_step}: {solving_message}")
        print(f"status: {'violated' if sudoku.violated else 'ok'}")
        print(self._prepare_string(
            sudoku,
            considered_tiles, considered_options,
            affected_tiles, affected_options))



_STEPPERS: Dict[str, Type[StepperBase]] = {
    "any": AnyStep,
    "skip": Skipper,
    "interesting": InterestingStep
}

def _create_solver(stepper: StepperBase) -> FmtSolvingMethod:
    return generate_solver(
        [
            ScaledXWing(2), 
            Bifurcation()
        ], stepper)


def solve(sudoku: Sudoku, stepping: str, flush: bool = False) -> Sudoku:
    """
    Solve a Sudoku given as `Sudoku` object (possibly obtained by the `load`
    function). Currently, the `formatting` parameter only takes 'console' as 
    possible value. You can choose between the steppers 'any', to render every
    solving step, 'skip' to completely suppress rendering, or 'interesting' to
    only print more elaborate solving methods. Use the `flush` parameter to 
    erase the rendered output of the previous solving step before continuing.
    """
    stepper = _STEPPERS[stepping](ConsoleFormatter(flush=flush), ConsoleTrigger())
    solver = _create_solver(stepper)
    s = solver.launch(sudoku)
    stepper.show(s)
    return s
