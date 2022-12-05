from __future__ import annotations

from typing import Callable
from abc import abstractmethod

from structure import Sudoku


class StepperBase:
    def __init__(self, formatting: Callable[[Sudoku, set, set, set, set], str]) -> None:
        self._fmt = formatting
    
    @abstractmethod
    def set_consideration(self, *args):
        pass

    @abstractmethod
    def show_step(self, *args):
        pass

    def show(self, sudoku: Sudoku):
        self._fmt(sudoku, set(), set(), set(), set())

class Skipper(StepperBase):
    pass

class AnyStep(StepperBase):
    _counter = 0
    solving_message: str

    def set_consideration(self, tiles: set, options: set, message: str):
       self.considered_tiles = tiles
       self.considered_options = options
       self.solving_message = message

    def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        self._counter += 1
        
        print("\033[H\033[J", end="")
        self._fmt(sudoku, self.considered_tiles, self.considered_options, affected_tiles, affected_options)
        print(f"solving step {self._counter}: {self.solving_message}")
        print(f"status: {'violated' if sudoku.violated else 'ok'}")

        answering = True
        while answering:
            if not input("next step: (press ENTER)"):
                answering = False
            else:
                print("JUST HIT ENTER!")
    
class InterestingStep(AnyStep):
    def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        
        return super().show_step(sudoku, affected_tiles, affected_options)
