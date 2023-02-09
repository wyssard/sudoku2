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
    def _get_defaults(self, considered_tiles, considered_options, affected_tiles, affected_options):
        return {
            "considered_tiles": considered_tiles if considered_tiles else set(),
            "considered_options": considered_options if considered_options else set(),
            "affected_tiles": affected_tiles if affected_tiles else set(),
            "affected_options": affected_options if affected_options else set()
        }

    @abstractmethod
    def render(self, 
        sudoku: Sudoku, 
        considered_tiles=None, 
        considered_options=None, 
        affected_tiles=None,
        affected_options=None, 
        solving_step: int = 0, 
        solving_message: str = None):
        """
        Print the Sudoku to the screen by the mean of your desire
        """
        return self._get_defaults(
            considered_tiles, considered_options,
            affected_tiles, affected_options)

class DeadFormatter(BlankFormatter):
    """
    Trivial formatter to raise an error when its `render` method is called.
    Such objects serve as default value for variables that take an object of 
    type `BlankFormatter` as value.
    """
    def render(self, *args):
        raise FormatterMissingError()
