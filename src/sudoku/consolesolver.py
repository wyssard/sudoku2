"""
Example module to illustrate a coupling of the solver to the console as 
frontend. Therefore, a corresponding `Trigger` and `Formatter` class must be
implemented.
"""

from __future__ import annotations

from typing import Set, Dict, Type

from .structure import Sudoku
from .stepping import NoTrigger, StepperBase, AnyStep, Skipper, InterestingStep
from .formatting import BlankFormatter
from .solvertools import generate_solver
from .solvingmethods import FmtSolvingMethod, ScaledXWing, Bifurcation

class ConsoleTrigger(NoTrigger):
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
    UNICODE_CHARS = {
        "H_LINE_CHAR": u"\u2500",
        "V_LINE_CHAR": u"\u2502",
        "CROSS_CHAR": u"\u253c",
        "LU_ANGLE": u"\u256d",
        "LL_ANGLE": u"\u2570",
        "RU_ANGLE": u"\u256e",
        "RL_ANGLE": u"\u256f",
        "L_T": u"\u251c",
        "R_T": u"\u2524",
        "U_T": u"\u252c",
        "D_T": u"\u2534"
    }

    ASCII_CHARS = {
        "H_LINE_CHAR": "-",
        "V_LINE_CHAR": "|",
        "CROSS_CHAR": "+",
        "LU_ANGLE": "+",
        "LL_ANGLE": "+",
        "RU_ANGLE": "+",
        "RL_ANGLE": "+",
        "L_T": "+",
        "R_T": "+",
        "U_T": "+",
        "D_T": "+"
    }
    

    def __init__(self, render_message=True, flush=False, unicode=True) -> None:
        self.flush = flush
        self.r_msg = render_message
        for key, value in self.UNICODE_CHARS.items() if unicode else self.ASCII_CHARS.items():
            self.__setattr__(key, value)

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

        row_strs += self._get_row_delimiter(self.LU_ANGLE, self.U_T, self.RU_ANGLE, square_width, self.H_LINE_CHAR)

        for row in range(9):
            col_strs = f"{self.V_LINE_CHAR} "
            for col in range(9):
                tile_index = 9*row+col
                tile = tiles[tile_index]

                in_tile_considered = set() if not tile_index in considered_tiles else tile.options&considered_options
                in_tile_affected = set() if not tile_index in affected_tiles else tile.options&affected_options

                col_strs += f"{self._format_tile(tile.options, in_tile_considered, in_tile_affected)}{(tile_width-tile.n_options*2-1)*' '}"
                
                if (c:=col+1)%3==0 and c < 9:
                    col_strs += f" {self.V_LINE_CHAR} "

            row_strs += f"{col_strs} {self.V_LINE_CHAR}\n"

            if (r:=row+1)%3==0 and r < 9:
                row_strs += self._get_row_delimiter(self.L_T, self.CROSS_CHAR, self.R_T, square_width, self.H_LINE_CHAR)

        row_strs += self._get_row_delimiter(self.LL_ANGLE, self.D_T, self.RL_ANGLE, square_width, self.H_LINE_CHAR)
        return row_strs

    def render(self, sudoku: Sudoku, considered_tiles=None, considered_options=None, affected_tiles=None, affected_options=None, solving_step: int = 0, solving_message: str = None):
        defaults = super().render(sudoku, considered_tiles, considered_options, affected_tiles, affected_options, solving_step, solving_message)
        if self.flush:
            print("\033[H\033[J", end="")
            
        print(f"solving step {solving_step}: {solving_message}")
        print(f"status: {'violated' if sudoku.violated else 'ok'}")
        print(self._prepare_string(sudoku, **defaults))


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


def solve(sudoku: Sudoku, stepping: str, flush: bool = False, unicode: bool = True) -> Sudoku:
    """
    Solve a Sudoku given as `Sudoku` object (possibly obtained by the `load`
    function). Use the `stepping` parameter to choose between the steppers 
    'any', to render every solving step, 'skip' to completely suppress 
    rendering, or 'interesting' to only print more elaborate solving methods. 
    Use the `flush` parameter to erase the rendered output of the previous 
    solving step before continuing.

    Args:
        sudoku: The puzzle to solve
        stepping: Specify what solving steps to render
        flush: Set to `True` to erase the previous solving step
        unicode: Use Unicode box-drawing characters

    Returns:
        The solved puzzle
    """

    stepper = _STEPPERS[stepping](ConsoleFormatter(flush=flush, unicode=unicode), ConsoleTrigger())
    solver = _create_solver(stepper)
    s = solver.launch(sudoku)
    stepper.show(s)
    return s
