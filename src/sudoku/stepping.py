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

from abc import abstractmethod

from .structure import Sudoku
from .formatting import BlankFormatter, DeadFormatter


class TriggerMissingError(NotImplementedError):
    """
    No trigger has been assigned to the stepper.
    """
    def __init__(self) -> None:
        super().__init__("no trigger has been assigned to the stepper")

class StepperMissingError(NotImplementedError):
    """
    No stepper has been assigned to the solving method. 
    """
    def __init__(self, method: str) -> None:
        super().__init__(f"no stepper has been set for solving method {method}")


class NoTrigger:
    """
    Classes that implement the functionality to await any sort uf user input
    after the puzzle has been rendered.
    """
    def trigger_next_step(self):
        """
        Trigger the next solving step.
        """
        pass

class DeadTrigger(NoTrigger):
    """
    Trivial trigger to raise an error when called. Such objects serve as 
    default argument for variables that take an object of type `NoTrigger` as
    value.
    """
    def trigger_next_step(self):
        raise TriggerMissingError()


class StepperBase:
    """
    Base class providing the template for any stepper by implementing a 
    solution-step counting mechanism and the interface to pass information about
    the current state of the puzzle through the stepper to the frontend.
    """
    def __init__(self, formatter: BlankFormatter = None, trigger: NoTrigger = None) -> None:
        """
        Create a stepper instance by passing a formatting function, i.e. a
        function to render the puzzle with additional information about the
        solving process
        """
        self.counter = 0
        self._fmt = formatter if formatter else DeadFormatter()
        self._trg = trigger if trigger else DeadTrigger()
    
    @abstractmethod
    def set_consideration(self, tiles: set, options: set, message: str, interesting: bool = False):
        """
        Interface method trough which the implementations of the solving 
        algorithms can pass to the frontend.
        """
        pass
    
    def _increase(self):
        self.counter += 1

    @abstractmethod
    def show_step(self, *args):
        """
        Invoke the frontend to print the current state of the Sudoku and 
        increase the solving step `counter` by one as this method is only called
        after a successful elimination of a candidate.
        """
        self._increase()

    def show(self, sudoku: Sudoku):
        """
        Use the selected formatter to render the Sudoku without any information
        about the solving process.
        """
        self._fmt.render(sudoku, 
            solving_step=self.counter, solving_message="puzzle solved")

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
    def __init__(self, formatter: BlankFormatter = None, trigger: NoTrigger = None) -> None:
        super().__init__(formatter, trigger)
    
class AnyStep(StepperBase):
    """
    Stepper class to transfer information about every elimination step to the
    frontend.
    """

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
        
    def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        self._increase()

        self._fmt.render(
            sudoku, 
            self.considered_tiles, 
            self.considered_options, 
            affected_tiles, 
            affected_options,
            self.counter,
            self.solving_message)
        self._trg.trigger_next_step()

class InterestingStep(AnyStep):
    """
    Stepper with functionality analogous to `AnyStep` but only solving steps
    whose importance was set to 'interesting' by means of the respective 
    argument of the `set_consideration` method are rendered.
    """
    def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        if self.interesting:
            return super().show_step(sudoku, affected_tiles, affected_options)
        else:
            self._increase()
