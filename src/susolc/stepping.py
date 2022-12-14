from __future__ import annotations

from typing import Callable
from abc import abstractmethod

from .structure import Sudoku


class StepperBase:
    def __init__(self, formatting: Callable[[Sudoku, set, set, set, set], str]) -> None:
        self._fmt = formatting
    
    @abstractmethod
    def set_consideration(self, tiles: set, options: set, message: str, interesting: bool = False):
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

    def set_consideration(self, tiles: set, options: set, message: str, interesting: bool = False):
       self.considered_tiles = tiles
       self.considered_options = options
       self.solving_message = message
       self.interesting = interesting

    def _step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        self._fmt(sudoku, self.considered_tiles, self.considered_options, affected_tiles, affected_options)
        print(f"solving step {self._counter}: {self.solving_message}")
        print(f"status: {'violated' if sudoku.violated else 'ok'}")

        answering = True
        while answering:
            if not input("next step: (press ENTER)"):
                answering = False
            else:
                print("JUST HIT ENTER!")

    def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        self._counter += 1
        self._step(sudoku, affected_tiles, affected_options)

class InterestingStep(AnyStep):
    def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        self._counter += 1
        if self.interesting:
            super()._step(sudoku, affected_tiles, affected_options)

class AnyStepFlush(AnyStep):
    def _step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        print("\033[H\033[J", end="")
        super()._step(sudoku, affected_tiles, affected_options)
        
class InterestingStepFlush(AnyStepFlush):
    def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        self._counter += 1
        if self.interesting:
            super()._step(sudoku, affected_tiles, affected_options)
