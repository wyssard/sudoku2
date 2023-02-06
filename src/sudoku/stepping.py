"""
This module provides the base for any 'stepper' class plus a few example
steppers used in the default solver. The steppers are devices used as backend 
for the formatted output of the solving process. Stepper objects provide an 
interface for the solving method classes to pass information about any 
successfully eliminated candidate. Moreover, they are able to pause the solving
process after any successful elimination to pass the latter information to any
frontend, thus enabling the user to step through the solving process, possibly
by means of a graphical output.
"""

from __future__ import annotations

from typing import Callable
from abc import abstractmethod

from .structure import Sudoku

class StepperMissingError(NotImplementedError):
    """
    No stepper has been assigned to the solving method. 
    """
    def __init__(self, method: str) -> None:
        super().__init__(f"no stepper has been set for solving method {method}")

class StepperBase:
    """
    Base class providing the template for any stepper by implementing a 
    solution-step-counting mechanism and the interface to pass information about
    the current state of the puzzle through the stepper to the frontend.
    """

    counter = 0

    def __init__(self, formatting: Callable[[Sudoku, set, set, set, set], str]) -> None:
        """
        Create a stepper instance by passing a formatting function, i.e. a
        function to render the puzzle with additional information about the
        solving process
        """
        self._fmt = formatting
    
    @abstractmethod
    def set_consideration(self, tiles: set, options: set, message: str, interesting: bool = False):
        """
        Interface method trough which the implementations of the solving 
        algorithms can pass to the frontend.
        """
        pass

    @abstractmethod
    def show_step(self, *args):
        """
        Invoke the frontend to print the current state of the Sudoku and 
        increase the solving step `counter` by one as this method is only called
        after a successful elimination of a candidate.
        """
        self.counter += 1

    def show(self, sudoku: Sudoku):
        """
        Use the selected formatter to print the current state of the Sudoku.
        """
        self._fmt(sudoku, set(), set(), set(), set())

class DeadStepper(StepperBase):
    """
    Trivial 'stepper' class serving as default value for any variable whose
    value must be of type `StepperBase`. That is, if no proper 'stepper' is
    assigned, this placeholder will raise an error whenever the user tries to 
    make use of the abstract methods that any stepper needs to implement.
    """
    def __init__(self, name: str) -> None:
        self._name = name

    def set_consideration(self, *args):
        raise StepperMissingError(self._name)

    def show_step(self, *args):
        raise StepperMissingError(self._name)

class Skipper(StepperBase):
    """
    Trivial stepper class that only counts the solving steps without invoking
    any rendering or interrupting the solving process.
    """
    pass

class AnyStep(StepperBase):
    """
    Stepper class to transfer information about every elimination step to the
    frontend.
    """

    solving_message: str

    def set_consideration(self, tiles: set, options: set, message: str, interesting: bool = False):
        """
        Tell the stepper what `options` of what `tiles` we're currently 
        considering to draw conclusions about what candidates we can eliminate.
        The `message` will be printed at a successful elimination. The
        `interesting` parameter specifies the complexity of the consideration. 
        """

        self.considered_tiles = tiles
        self.considered_options = options
        self.solving_message = message
        self.interesting = interesting

    def _step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        self._fmt(sudoku, self.considered_tiles, self.considered_options, affected_tiles, affected_options)
        print(f"solving step {self.counter}: {self.solving_message}")
        print(f"status: {'violated' if sudoku.violated else 'ok'}")

        answering = True
        while answering:
            if not input("next step: (press ENTER)"):
                answering = False
            else:
                print("JUST HIT ENTER!")

    def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        super().show_step()
        self._step(sudoku, affected_tiles, affected_options)

class AnyStepFlush(AnyStep):
    """
    
    """

    def _step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        print("\033[H\033[J", end="")
        super()._step(sudoku, affected_tiles, affected_options)

def _get_interesting_step_classes(base: type):
    class InterestingStepBase(base):
        def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
            self.counter += 1
            if self.interesting:
                super()._step(sudoku, affected_tiles, affected_options)
    return InterestingStepBase
    
InterestingStep = _get_interesting_step_classes(AnyStep)
InterestingStepFlush = _get_interesting_step_classes(AnyStepFlush)
