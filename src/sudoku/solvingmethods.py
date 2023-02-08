"""
Core module of the solver, providing the structure of the different solving
algorithms by means of the base classes `FmtSolvingBase` and 
`FmtSolvingMethod`. These classes work as templates for the integration
of the specific solving algorithms through their child classes but also provide 
the abstract interface to access these algorithms. 

Use this module to integrate your own solving algorithms to this solver or to
access the four default solving methods: `NTilesNOptions`, `ScaledXWing`, 
`YWing` and `Bifurcation`.

Moreover, this file also provides the device required to remove candidates from 
Sudoku tiles. Observe that the implemented algorithms are not able to solve the 
puzzle on their own but depend on a prescription of what algorithm to use in the 
specific state of the puzzle. This logic is implemented by means of any 
solving-method class having attributes that link to other solving-method classes
which are to be used depending on the success or failure of the present solving 
algorithm. The linking of the solving methods is done via the `generate_solver` 
function found in `solver.py`
"""

from __future__ import annotations

from .structure import Sudoku, Tile, CONTAINER_TYPES
from .stepping import StepperBase, DeadStepper
from .formatting import CONTAINER_NAMES

from abc import abstractmethod
from typing import Set, List, Tuple
from copy import deepcopy


class SolverError(RuntimeError):
    """
    The puzzle can't be solved with the given solver.
    """
    def __init__(self) -> None:
        super().__init__("could not solve puzzle with the solving methods given")

class RemoverMissingError(NotImplementedError):
    """
    No remover has been assigned to the solving method.
    """
    def __init__(self, method: str) -> None:
        super().__init__(f"no remover has been set for solving method {method}")

class StepperMissingError(NotImplementedError):
    """
    No stepper has been assigned to the solving method. 
    """
    def __init__(self, method: str) -> None:
        super().__init__(f"no stepper has been set for solving method {method}")


class FmtSolvingBase:
    """
    Class to define the basic structure of any object the Sudoku solver 
    consists of. Such child classes must always implement a `launch` method 
    which, in the case of the `RemoveAndUpdate` class, invokes the removal 
    process whereas in the case of any regular solving method (i.e. of any 
    class inheriting from `FmtSolvingMethod`), the respective solving algorithm
    will be invoked.

    Any such class has a `_stepper` attribute which is the tool needed to guide
    the user through the solving process and to collect information thereof.
    """

    def __init__(self, stepper: StepperBase = None) -> None:
        self._stepper = stepper if stepper else DeadStepper(self.__class__.__name__)

    def set_stepper(self, stepper: StepperBase):
        self._stepper = stepper

    @abstractmethod
    def launch(self, S: Sudoku, *args):
        """
        Interface method to invoke the internals of the corresponding solving
        algorithm.
        """
        pass

class _DeadRemover(FmtSolvingBase):
    """
    Trivial 'Remover' class to raise an error when its `launch` method is called.
    Instances of this class can be used as default value for variables that 
    serve as 'Remover', thus telling the user that no proper 'Remover' has been
    specified.
    """
    def __init__(self, name) -> None:
        self._name = name

    def launch(self, *args):
        raise RemoverMissingError(self._name)

class _SolvingFail(FmtSolvingBase):
    """
    Trivial 'Solving-Method' whose `launch` method is invoked when all its
    precedent solving algorithms failed. This method will thus raise an error and
    terminate the solving process. 
    """
    def __init__(self):
        pass

    def launch(self, S: Sudoku):
        raise SolverError()


class FmtSolvingMethod(FmtSolvingBase):
    """
    Base class to define the structure of the solver. 
    
    Any class inheriting from this base represents an algorithm used to 
    eliminate candidate options from the unsolved puzzle. 
    
    The implementation of these algorithms happens by means of overloading the 
    abstract `launch` method. This method, taking the unsolved puzzle as 
    argument, executes the corresponding solving algorithm and depending on 
    its success decides what solving method to try next. That is, if the present
    algorithm succeeds at eliminating at least one candidate option, then the 
    `launch` method of the `_advance` attribute is invoked. On the other hand, 
    if the present algorithm fails at removing candidates, the unsolved puzzle 
    is passed to the `launch` implementation of the `_fall_back` attribute.
    Both, the `_advance` and the `_fall_back` object must therefore be an 
    instances of a children of `FmtSolvingMethod` themselves.

    If none of the implemented solving methods (i.e. non of the instances of
    the corresponding children of `FmtSolvingMethod`) manage to contribute to 
    the solution, the puzzle must be considered unsolvable. Therefore, the 
    `_fall_back` attribute defaults to `_SolvingFail()` which is a trivial 
    child of `FmtSolvingMethod` whose `launch` method raises an error. Hence, if 
    any solving-method object does not explicitly link a `_fall_back` instance,
    it is automatically considered to represent the worst case algorithm to be 
    tried as its failure implies the insolubility of the puzzle by this solver.
    """

    def __init__(self, stepper: StepperBase = None, remover: RemoveAndUpdate = None) -> None:
        super().__init__(stepper)
        self._remove = remover if remover else _DeadRemover(self.__class__.__name__)
        self._advance = self
        self._fall_back = _SolvingFail()

    def set_remover(self, remover: RemoveAndUpdate):
        self._remove = remover

    def set_fall_back(self, fall_back: FmtSolvingMethod):
        self._fall_back = fall_back

    def set_advance(self, advance: FmtSolvingMethod):
        self._advance = advance

    @abstractmethod
    def launch(self, S: Sudoku):
        pass

class FmtParamSolvingMethod(FmtSolvingMethod):
    """
    Base class for solving methods that depend on a parameter. The minimum value
    the parameter takes is specified by the `_N_MIN` class variable which varies
    between the different solving method classes that inherit from the present
    class. 

    The solving method's parameter is set at initialization of any such object; 
    if the given parameter is smaller than `_N_MIN`, a corresponding error
    terminates the program.
    """

    _N_MIN = 1

    def __init__(self, param: int, stepper: StepperBase = None, remover: RemoveAndUpdate = None) -> None:
        super().__init__(stepper, remover)
        if param >= self._N_MIN:
            self._n = param
        else:
            raise ValueError(f"parameter of {self.__class__.__name__} solving method must be larger or equal to {self._N_MIN} but {param} is given")



class RemoveAndUpdate(FmtSolvingBase):
    """
    Special solving-method class whose `launch` method implements the 
    functionality to remove candidates from specified tiles. 
    Correspondingly, this method should be invoked by the 'regular' 
    solving-method objects, i.e., by instances of classes that inherit from 
    `FmtSolvingMethod`.

    Moreover, the removal process also triggers the clean up methods
    `_single_occurrence_of_option` and `_remove_option_from_neighbors` which
    implement further candidate removal steps that are directly implied by the
    initial removal.
    """

    def _single_occurrence_of_option(self, S: Sudoku, tile_index: int, remove_options: set):
        """
        There is the possibility that one of the `remove_options` we removed 
        from the tile at `tile_index` has been shared with a single other tile
        that lives, e.g., in the same row. Hence, after the removal, this latter
        tile is the only one in the row that still exhibits the concerned 
        candidate such that its value can immediately be fixed
        """
        
        tile = S.tiles[tile_index]
        for kind in CONTAINER_TYPES:
            occurrence = S.occurrences[kind][tile.pos[kind]]
            for o in remove_options:
                if len(occurrence[o-1]) == 1:
                    where_only_one_left: int = list(occurrence[o-1])[0]
                    remove_opts = deepcopy(S.tiles[where_only_one_left].options)-{o}

                    self._stepper.set_consideration(
                        {where_only_one_left},
                        {o},
                        f"tile {where_only_one_left} is the only tile in {CONTAINER_NAMES[kind]} {tile.pos[kind]+1} with {o} as option",
                        True)
                    
                    self.launch(S, where_only_one_left, remove_opts)
                
                if S.violated:
                    return False

        return True

    def _remove_option_from_neighbors(self, S: Sudoku, tile_index: int):
        """
        After having removed the specified candidates from the tile at 
        `tile_index`, the concerned tile may have only one candidate left, i.e.
        its value is fixed by the previous removal. Therefore, its value must
        not be considered a candidate of any neighboring tile anymore.
        """

        tile = S.tiles[tile_index]
        for kind in CONTAINER_TYPES:
            container = S.containers[kind][tile.pos[kind]]
            for t_idx in set(container)-{tile_index}:
                
                self._stepper.set_consideration(
                    {tile_index},
                    tile.options,
                    f"value of tile {tile_index} has been fixed to {tile.options}, thus removing this option from tile {t_idx}",
                    False)

                self.launch(S, t_idx, tile.options)
                
                if S.violated:
                    return False
        
        return True

    def _update_chain_removal(self, S: Sudoku, tile_index: int, remove_options: set):
        """
        Intermediate method, to invoke the clean up methods after the removal
        of the `remove_options` from the tile at `tile_index`.
        """

        tile = S.tiles[tile_index]
        if not self._single_occurrence_of_option(S, tile_index, remove_options):
            return False

        if tile.n_options == 1:
            tile.solved_at = self._stepper.counter
            if not self._remove_option_from_neighbors(S, tile_index):
                return False

        return True


    def _update_occurrences(self, S: Sudoku, tile_index: int, remove_options: set):
        """
        After removing `remove_options` from the tile at `tile_index`, we need
        to make sure that this `tile_index` is no longer registered as a
        position at which any of the candidates in `remove_options` occur.
        """

        tile = S.tiles[tile_index]
        for kind in CONTAINER_TYPES:
            occurrence = S.occurrences[kind][tile.pos[kind]]
            for o in remove_options:
                occurrence[o-1] -= {tile_index}
                if len(occurrence[o-1]) == 0:
                    S.violated = True
                    return False
        
        return True
    
    def _update_and_check_violations(self, S: Sudoku, tile_index: int, remove_options: set):
        """
        Invoke the process to update the lists that register at which positions
        which candidates occur and check if Sudoku rules are violated by 
        verifying that the manipulated tile at `tile_index` still has more than
        zero candidates left.
        """

        if S.tiles[tile_index].n_options > 0:
            if self._update_occurrences(S, tile_index, remove_options):
                return True
        
        S.violated = True
        return False

    def _remove_and_check_violations(self, S: Sudoku, where: int, which: set) -> bool:
        """
        Remove the candidates `which` from the tile at `where`.
        """

        self._stepper.show_step(S, {where}, which)
        S.tiles[where].options -= which
        return self._update_and_check_violations(S, where, which)


    def launch(self, S: Sudoku, where: int, which: set) -> bool:
        tile = S.tiles[where]
        if (diff:=tile.options&which):
            if self._remove_and_check_violations(S, where, diff):
                return self._update_chain_removal(S, where, diff)
            else:
                return False
        else:
            return False


class NTilesNOptions(FmtParamSolvingMethod):
    """
    A solving method that checks if a set of the same `n` options is found `n`
    times in the same row, column or square. If, e.g., the set of candidate
    options `{1,2}` is found twice in the same row, i.e., if two separate tiles
    have the exact same two candidates left, no other tile in the same row may
    take any of the latter two values.
    """

    _N_MIN = 1

    def _get_solving_message(self, n: int, kind: str, c_index: int, matches: set, shared_options: set):
        c_name = CONTAINER_NAMES[kind]
        if n==1:
            return f"tile {matches} in {c_name} {c_index} has fixed value {shared_options}; this option is thus removed from the remaining tiles in {c_name} {c_index}"
        else:
            return f"tiles {matches} in {c_name} {c_index} share options {shared_options}; removing these options from the remaining tiles in {c_name} {c_index}"

    def _get_equivalent_tiles(self, S: Sudoku, where: Set[int], tile_index: int) -> Set[int]:
        """
        return indices of all tiles within `where` that have the same options 
        as the tile at `which` 
        (`which` is also included)
        """
        
        if (tile:=S.tiles[tile_index]).n_options == 1:
            return {tile_index}

        else:
            matches = set()
            for tile_index in where:
                if S.tiles[tile_index].options == tile.options:
                    matches.add(tile_index)
            return matches if len(matches)==tile.n_options else set()

    def _n_times_n_options_removal_container(self, S: Sudoku, kind: str, container_index: int, n: int) -> bool:
        success = False
        container = S.containers[kind][container_index]
        
        for tile_index in container:
            if len(matches:=self._get_equivalent_tiles(S, container, tile_index)) == n:
                
                shared_options = S.tiles[tile_index].options

                for unmatched in set(container)-matches:
                    self._stepper.set_consideration(
                        matches,
                        shared_options,
                        self._get_solving_message(n, kind, container_index, matches, shared_options),
                        n>1)
                        
                    if self._remove.launch(S, unmatched, shared_options):
                        success = True

                    if S.violated:
                        return False

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

                    if self._n_times_n_options_removal_container(S, kind, kind_index, self._n):
                        success = True
                        # return self._advance.launch(S)

            if success:
                return self._advance.launch(S)
            else:
                return self._fall_back.launch(S)

class ScaledXWing(FmtParamSolvingMethod):
    """
    Solving methods that searches for candidate options appearing in an 
    `n` x `n` square. 
    
    Consider, e.g., two columns in which the same candidate occurs at exactly 
    two positions. Now, let the rows in which these occurrences are to be the same 
    for both columns. Then non of the remaining tiles within the latter tow rows 
    can take this candidate as value anymore as its position is already fixed to
    a place in either of the tow columns we considered initially.
    """
    _N_MIN = 2

    def _find_option_in_n_by_n(self, S: Sudoku, n: int, primary_kind: str, option: int) -> List[Set[int]]:
        primary_kind_tiles: List[Set[int]] = []
        secondary_kind, = {"r", "c"}-{primary_kind}
        secondary_to_consider: List[Set[int]] = []
        for occurrence in S.occurrences[primary_kind]:
            if len(tile_idxs:=occurrence[option-1]) == n:
                primary_kind_tiles.append(tile_idxs)
                secondary_pos = {S.tiles[idx].pos[secondary_kind] for idx in tile_idxs}
                secondary_to_consider.append(secondary_pos)
                if secondary_to_consider.count(secondary_pos) == n:
                    return [primary_kind_tiles[i] for i, sc_pos in enumerate(secondary_to_consider) if sc_pos==secondary_pos]

        return None
        
    def _option_in_n_by_n_removal(self, S: Sudoku, n: int, primary_kind: str, option: int):
        throw_away = set()
        secondary_kind, = {"r", "c"}-{primary_kind}
        if (primary_kind_tiles:=self._find_option_in_n_by_n(S, n, primary_kind, option)):
            found_tiles = {idx for idxs in primary_kind_tiles for idx in idxs}
   
            for t_idx in primary_kind_tiles[0]:
                tile = S.tiles[t_idx]
                secondary_kind_occurrence = S.occurrences[secondary_kind][tile.pos[secondary_kind]]
                secondary_kind_tiles = secondary_kind_occurrence[option-1]
                throw_away |= (secondary_kind_tiles - found_tiles)
            
            if len(throw_away) > 0:
                for t_idx in throw_away:
                    self._stepper.set_consideration(
                        found_tiles,
                        {option},
                        f"found option {option} in {n}x{n} square at {found_tiles}, thus removing {option} from {t_idx}",
                        True)

                    self._remove.launch(S, t_idx, {option})
                    if S.violated:
                        return False

                return True

            else:
                return False     

    def launch(self, S: Sudoku):
        success = False
        if S.done:
            return S
        else:
            for direction in ("r", "c"):
                for option in range(1, 10):
                    if S.violated:
                        return False

                    if self._option_in_n_by_n_removal(S, self._n, direction, option):
                        success = True
        
            if success:
                return self._advance.launch(S)
            else:
                return self._fall_back.launch(S)

class YWing(FmtSolvingMethod):
    """
    Implementation of the *classical* 'Y-Wing' strategy.

    This methods first searches for an 'anchor' tile, i.e., a tile with two
    candidates left, say `{1,2}`. From this tile on, the neighboring row, column
    and square are searched for further 'two-candidate' tiles. The aim, thereby,
    is to find two more tiles, one of them including `1` and the other `2` as 
    candidate. Most importantly these two tiles must also have one common candidate,
    say `3`, such that we end up with two 'node' tiles related to the anchor,
    having candidates `{1,3}` and `{2,3}`. No matter what configuration 
    eventually solves the puzzle, one of the node tiles must be
    assigned the value `3` as fixing the value of one node immediately fixes
    the value of the other node via the anchor tile. Consequently, `3` can 
    be excluded as candidate from any tile that is simultaneously related to 
    both nodes.
    """

    def _get_node_candidates(self, S: Sudoku, anchor: Tile):
        candidates = set()
        for kind in CONTAINER_TYPES:
            for t_idx in S.containers[kind][anchor.pos[kind]]:
                tile = S.tiles[t_idx]
                if (tile.n_options==2) and (len(tile.options&anchor.options) == 1):
                    candidates.add(t_idx)

        candidates = list(candidates)
        return candidates
    
    def _eliminate_candidates(self, S: Sudoku, anchor: Tile, candidates: List[int]) -> List[Tuple[int, int]]:
        n_candidates = len(candidates)
        if n_candidates < 2:
            return []

        valid_pairs = []

        for lcn in range(n_candidates-1):
            left = S.tiles[candidates[lcn]]
            for rcn in range(lcn+1, n_candidates):
                right = S.tiles[candidates[rcn]]
                
                if (anchor.options.issubset(right.options|left.options)) and (len(right.options&left.options) == 1):
                    valid_pairs.append((candidates[lcn], candidates[rcn]))
        
        return valid_pairs

    def _get_tile_range(self, S: Sudoku, tile: Tile):
        tile_range = set()
        for kind in CONTAINER_TYPES:
            tile_range |= set(S.containers[kind][tile.pos[kind]])
        return tile_range

    def _find_y_wing_and_remove(self, S: Sudoku, anchor_index: int):
        anchor = S.tiles[anchor_index]
        valid_pairs = self._eliminate_candidates(S, anchor, self._get_node_candidates(S, anchor))
        for pair in valid_pairs:
            l, r = pair
            l_tile = S.tiles[l]
            r_tile = S.tiles[r]
            considered_nodes = {l, r, anchor_index}
            common_range = (self._get_tile_range(S, l_tile)&self._get_tile_range(S, r_tile))-considered_nodes

            if len(common_range)==0:
                return False
            
            else:
                success = False

                common_option = l_tile.options&r_tile.options
                for target in common_range:
                    self._stepper.set_consideration(
                        considered_nodes, anchor.options|l_tile.options|r_tile.options, 
                        f"found Y-Wing with anchor at {anchor_index} and nodes at {l}, {r}, remove the shared option {common_option} from {target}",
                        True)
                    
                    if self._remove.launch(S, target, common_option):
                        success = True
                    if S.violated:
                        return False

                return success
            
    def launch(self, S: Sudoku):
        success = False
        if S.done:
            return S
        else:
            for anchor in filter(lambda idx: S.tiles[idx].n_options==2, range(81)):
                if S.violated:
                    return False
                
                if self._find_y_wing_and_remove(S, anchor):
                    success = True
                    # return self._advance.launch(S)
            
            if success:
                return self._advance.launch(S)
            else:
                return self._fall_back.launch(S)

class Bifurcation(FmtSolvingMethod):
    """
    The uninspired emergency solving method.

    After failure of the previous algorithms, we may still fall back to a trial
    and error approach by considering tiles with two candidates left and by
    mindlessly picking one of them as the tiles value. From there on, we can 
    continue solving the puzzle with the 'more analytic' methods until we 
    either solve to puzzle or run into a violation of the Sudoku rules. Since
    we only apply this approach to 'two-candidate' tiles, a failure of the try
    still immediately fixes the definitive value of the considered tile.
    """

    def launch(self, S: Sudoku):
        for tile_index in range(81):
            tile = S.tiles[tile_index]
            if tile.n_options == 2:

                opts = deepcopy(tile.options)
                
                backup = deepcopy(S)
                try_option = opts.pop()
                alt_option = opts.pop()

                self._stepper.set_consideration(
                    {tile_index},
                    {alt_option},
                    f"bifurcation at {tile_index}; try {alt_option}",
                    True)
                
                self._remove.launch(backup, tile_index, {try_option})
                if not (out:=self._advance.launch(backup)):
                    

                    self._stepper.set_consideration(
                        {tile_index},
                        {try_option},
                        f"bifurcation at {tile_index} with {alt_option} failed, go with {try_option} instead",
                        True)

                    backup = deepcopy(S)
                    self._remove.launch(backup, tile_index, {alt_option})
                    out = self._advance.launch(backup)

                return out
    
        return self._fall_back.launch(S)

