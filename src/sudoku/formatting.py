"""
This module provides the base class for `Formatter` objects.
"""

from __future__ import annotations

from abc import abstractmethod

from .structure import Sudoku

CONTAINER_NAMES = {
    "r": "row",
    "c": "column",
    "s": "square"
}

class FormatterMissingError(NotImplementedError):
    """
    No formatter has been assigned to the stepper.
    """
    def __init__(self) -> None:
        super().__init__("no formatter has been assigned to the stepper")


class BlankFormatter:
    """
    Formatters implement the `render` method called by any stepper to print the
    progress of the solver to the screen by any means.
    """
    @abstractmethod
    def render(self, 
        sudoku: Sudoku, 
        considered_tiles: set, 
        considered_options: set, 
        affected_tiles: set,
        affected_options: set, 
        previously_involved: set,
        solving_step: int, 
        solving_message: str):
        """
        Print the Sudoku to the screen by the mean of your desire
        """
        pass

class DeadFormatter(BlankFormatter):
    """
    Trivial formatter to raise an error when its `render` method is called.
    Such objects serve as default value for variables that take an object of 
    type `BlankFormatter` as value.
    """
    def render(self, *args):
        raise FormatterMissingError()
