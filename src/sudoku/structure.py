"""
This module provides the two classes `Tile` and `Sudoku` that serve as base
structure for the solver to operate on. Observe that the abbreviations 'r',
'c' and 's' for row, column and square, stored in `CONTAINER_TYPES`, are used
throughout this program. Square, thereby, refers to typical 3x3 tile 
collections.
"""

from __future__ import annotations

from typing import Dict, List, Set

CONTAINER_TYPES = ("r", "c", "s")

def row_column_to_index(r: int, c: int) -> int:
    """
    Get the tile index, i.e. the position of the tile in an array of dimension
    `81`, by specifying the row `r` and the column `c`.

    Args:
        r: Row index
        c: Column index

    Returns:
        Tile index
    """
    return r*9+c

def index_to_pos(t: int) -> Dict[str, int]:
    """
    Get the row, column and square index from the tile index `t` formatted as 
    `{'r': *row index*, 'c': *column index*, 's': *square index*}`.

    Args:
        t: The tile index

    Returns:
        Dict containing row, column and square index
    """
    return {"r": (r:=t//9), "c": (c:=t%9), "s": 3*(r//3) + c//3}

class Tile:
    """
    Structure to represent a tile of the Sudoku grid. Tile objects store the 
    position of a tile by means of specifying their row, column and square 
    index. Moreover, this class is needed to keep track of the possible 
    candidate values a tile can still take in the process of solving the puzzle.
    """
    def __init__(self, r: int, c: int, s: int) -> None:
        self._pos = {"r": r, "c": c, "s": s}
        self._options = set(range(1, 10))
        self.n_options = 9
        self.solved_at = 0

    def __getitem__(self, key: str):
        return self._pos[key]

    @property
    def pos(self) -> Dict[str, int]:
        """
        Get the row, column and square index of the tile formatted as
        `{'r': *row index*, 'c': *column index*, 's': *square index*}`.

        Returns:
            The row, column and square index of the tile
        """
        return self._pos

    @property
    def options(self) -> set:
        """
        Returns:
            The remaining candidate values for this tile 
        """
        return self._options

    @options.setter
    def options(self, new_options) -> None:
        self._options = new_options
        self.n_options = len(new_options)

    @classmethod
    def to_none_tile(cls, tile: Tile) -> Tile:
        """
        Create a tile that has no candidate values at the position of the 
        `tile` that is given as argument.
        """
        obj = super().__new__(cls)
        obj._pos = tile._pos
        obj._options = {}
        obj.n_options = 0
        return obj

class Sudoku:
    """
    Container structure to represent the Sudoku grid by storing 81 `Tile` 
    objects in a one dimensional list. 
    """
    def __init__(self, content: List[int]) -> None:
        self.violated = False

        self._tiles: List[Tile] = []
        self._containers: Dict[str, List[List[int]]] = {}
        self._occurrences: Dict[str, List[List[Set[int]]]] = {}

        for kind in CONTAINER_TYPES:
            self._occurrences[kind] = [[set() for _ in range(9)] for _ in range(9)]
            self._containers[kind] = [[] for _ in range(9)]

        given_tiles: List[int] = []
        for tile_index in range(81):
            tile = Tile(**index_to_pos(tile_index))
            if val:=content[tile_index]:
                tile.options = {val}
                given_tiles.append(tile_index)

            for kind in CONTAINER_TYPES:
                self._containers[kind][tile.pos[kind]].append(tile_index)

                occurrence = self._occurrences[kind][tile.pos[kind]]
                for o in tile.options:
                    occurrence[o-1].add(tile_index)
                
            self._tiles.append(tile)

        for tile_index in given_tiles:
            tile = self._tiles[tile_index]

            # option 'o' has occurrence position 'o-1'
            option_occurrence_pos = list(tile.options)[0]-1

            for kind in CONTAINER_TYPES:
                occurrence = self._occurrences[kind][tile.pos[kind]]
                occurrence[option_occurrence_pos] = {tile_index}

    @property
    def max_options(self) -> int:
        """
        Returns:
            The maximum number of candidates over all the tiles
        """
        return max(tile.n_options for tile in self._tiles)

    @property
    def done(self) -> bool:
        """
        Returns: 
            Whether the puzzle is solved
        """
        return True if self.max_options==1 and not self.violated else False

    @property
    def tiles(self) -> List[Tile]:
        """
        Returns:
            List of length 81 to store every tile of the Sudoku grid.
        """
        return self._tiles

    @property
    def containers(self) -> Dict[str, List[List[int]]]:
        """
        Structure to store the indices of the tiles, i.e. their position in the
        `tiles` array, that live in each row, column and square. 
        
        Consider the following example to retrieve the array positions of the 
        tiles that live in the first square:
        
        Examples:
            >>> Sudoku.containers['s'][0]
            [0, 1, 2, 9, 10, 11, 18, 19, 20]

        Thereby, the subscript `['s'][0]` indicates the square at position 0.

        Returns:
            The containers (as described above)
        """
        return self._containers

    @property
    def occurrences(self) -> Dict[str, List[List[Set[int]]]]:
        """
        For each row, column and square and for each number of 1 to 9, this 
        dictionary stores at which `tiles` positions the respective value still 
        appears as candidate.

        Consider the following example to retrieve the set of array positions at 
        which the candidate `9` is still found in the second row:

        Examples:
            >>> Sudoku.occurrences['r'][1][8]
            {9, 11, 15}

        Thereby, `['r'][1]` indicates the second row and `[8]` specifies the 
        list position at which the occurrences of the value `9` are stored.

        Returns:
            The occurrences (as above duh xD)
        """
        return self._occurrences

    def is_valid(self) -> bool:
        """
        Explicitly check whether the Sudoku rules have been violated in the 
        solving process. One should try to avoid explicit use of this method as
        the implementations of the solving algorithms should automatically 
        detect if such a violation has been taken place and correspondingly set 
        the `violated` attribute to `True`.

        Returns:
            Is the present configuration valid?
        """
        if not self.violated:
            goal = set(range(1,10))
            for kind in CONTAINER_TYPES:
                for i in range(9):
                    container = self._containers[kind][i]
                    options = set()
                    for tile_index in container:
                        options |= self._tiles[tile_index].options
                    
                    if not options == goal:
                        print(f"error at {kind} {i}")
                        return False
            
            return True
        else:
            return False

    def get_tiles(self) -> List[List[Tile]]:
        """
        Returns:
            The tiles organized row by row
        """
        return [[t for t in self._tiles[9*r:9*(r+1)]] for r in range(9)]

    def get_options(self) -> List[List[set]]:
        """
        Returns:
            The remaining candidates for each tile as set organized row by row
        """
        return [[t.options for t in self._tiles[9*r:9*(r+1)]] for r in range(9)]

    def get_solved(self) -> List[List[int]]:
        """
        Returns: 
            The solved puzzle as a two-dimensional list.
        """
        if self.done:
            return [[list(tile.options)[0] for tile in row] for row in self.get_tiles()]
        else:
            raise RuntimeError("Puzzle is not solved yet.")
         
    def get_complexity_map(self) -> List[List[int]]:
        """
        Returns: 
            The solving step a which the definite solution has been found 
            for each tile (organized row by row).
        """
        return [[tile.solved_at for tile in row] for row in self.get_tiles()]