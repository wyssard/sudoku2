# API Guide

This guide walks you through the creation of solving method, stepper and formatting classes. The respective instances can then be composed to a solver object by following the procedure illustrated in the [Custom Solver section](custom_solver.md). Make sure to consider the latter section first before continuing with this guide.

The creation of the **solving method**, **stepper** and **formatting** classes is thereby illustrated by reproducing classes that are already integral part of this package. To avoid duplicate code, there's no example code for the largest part of this guide. We only provide a small snippet to illustrate the usage of the classes you are to create thereinafter.

## Solving Methods

Let us begin by reimplementing the most basic of all solving methods. 

```py linenums="1"
class LoneSingles(FmtSolvingMethod):
    """
    The most basic solving method that is used to initiate the solving process.
    This method simply searches for the tiles whose value has already been 
    fixed and removes the respective number from its neighboring tiles.
    """

    def _lone_single_in_kind(self, S: Sudoku, kind: str, container_index: int):
        success = False
        container = S.containers[kind][container_index]
        for tile_index in container:
            tile = S.tiles[tile_index]
            if tile.n_options == 1:
                for affected in set(container)-{tile_index}:
                    if S.violated:
                        return False
                    
                    self._stepper.set_consideration(
                        {tile_index}, tile.options, 
                        f"""the value of tile {tile_index} was fixed to 
                        {tile.options}; this option is thus removed from the 
                        remaining tiles in 
                        {CONTAINER_NAMES[kind]} {container_index}""",
                        False)

                    if self._remove.launch(S, affected, tile.options):
                        success = True 
        return success

    def launch(self, S: Sudoku):
        success = False
        if S.done:
            return S
        else:
            for kind in CONTAINER_TYPES:
                for kind_index in range(9):
                    if S.violated:
                        return False
                    
                    if self._lone_single_in_kind(S, kind, kind_index):
                        success = True
            
            if success:
                return self._advance.launch(S)
            else:
                return self._fall_back.launch(S)
```

## Steppers

```py linenums="1"
class AnyStep(StepperBase):
    """
    Stepper class to transfer information about every elimination step to the
    frontend.
    """

    def set_consideration(self, tiles: set, options: set, message: str, interesting: bool = False):
        self.considered_tiles = tiles
        self.considered_options = options
        self.solving_message = message
        self.interesting = interesting
        
    def show_step(self, sudoku: Sudoku, affected_tiles: set, affected_options: set):
        """
        Invoke the render to print the solving step based on the previously
        specified [consideration][sudoku.stepping.StepperBase.set_consideration].

        Args:
            sudoku: The concerned puzzle
            affected_tiles: The tiles affected by the present configuration
                            of the neighboring tiles
            affected_options: The candidate to be removed from the latter tiles 
        """

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

```

## Formatters

```py linenums="1"


```

## Assembly