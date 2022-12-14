from __future__ import annotations

from .structure import Sudoku, Tile, CONTAINER_TYPES
from .stepping import StepperBase
from .formatting import CONTAINER_NAMES

from abc import abstractmethod
from typing import Set, List, Tuple
from copy import deepcopy


class FmtSolvingBase:
    def __init__(self, stepper: StepperBase) -> None:
        self._stepper = stepper

    @abstractmethod
    def launch(self, S: Sudoku, *args):
        pass

class _SolvingFail(FmtSolvingBase):
    def __init__(self):
        pass

    def launch(self, S: Sudoku):
        return False

class FmtSolvingMethod(FmtSolvingBase):
    def __init__(self, stepper: StepperBase, remove: RemoveAndUpdate) -> None:
        super().__init__(stepper)
        self._remove = remove
        self._advance = self
        self._fall_back = _SolvingFail()

    def set_fall_back(self, fall_back: FmtSolvingMethod):
        self._fall_back = fall_back

    def set_advance(self, advance: FmtSolvingMethod):
        self._advance = advance

    @abstractmethod
    def launch(self, S: Sudoku):
        pass

class FmtParamSolvingMethod(FmtSolvingMethod):
    N_THRESHOLD: int
    N_INIT: int
    _n: int


class RemoveAndUpdate(FmtSolvingBase):
    def _counter_update_chain(self, S: Sudoku, tile_index: int, remove_options: set):
        tile = S.tiles[tile_index]
        for kind in CONTAINER_TYPES:
            counter = S.counters[kind][tile.pos[kind]]
            for o in remove_options:
                if len(counter[o-1]) == 1:
                    where_only_one_left = list(counter[o-1])[0]
                    remove_opts = deepcopy(S.tiles[where_only_one_left].options)-{o}

                    self._stepper.set_consideration(
                        {where_only_one_left},
                        {o},
                        f"tile {where_only_one_left} is the only tile in {CONTAINER_NAMES[kind]} {tile.pos[kind]+1} with {o} as option")
                    
                    if not self.launch(S, where_only_one_left, remove_opts):
                        return False
        return True

    def _update_counter(self, S: Sudoku, tile_index: int, remove_options: set):
        tile = S.tiles[tile_index]
        for kind in CONTAINER_TYPES:
            counter = S.counters[kind][tile.pos[kind]]
            for o in remove_options:
                counter[o-1] -= {tile_index}
                if len(counter[o-1]) == 0:
                    S.violated = True
                    return False

        return self._counter_update_chain(S, tile_index, remove_options)
        
    def launch(self, S: Sudoku, where: int, which: set) -> bool:
        tile = S.tiles[where]
        if (diff:=tile.options & which):
            
            self._stepper.show_step(S, {where}, which)

            tile.options -= which
            if tile.n_options > 0:
                return self._update_counter(S, where, diff)
                
        else:
            return False


class NTilesNOptions(FmtParamSolvingMethod):
    N_THRESHOLD = 3
    N_INIT = 1
    _n = N_INIT

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
        if S.done:
            # self._stepper.show(S)
            return S
        else:
            for kind in CONTAINER_TYPES:
                for kind_index in range(9):
                    if S.violated:
                        return False

                    if self._n_times_n_options_removal_container(S, kind, kind_index, self._n):
                        self._n = self.N_INIT
                        return self._advance.launch(S)

            if self._n < self.N_THRESHOLD:
                self._n += 1
                return self.launch(S)
            else:
                self._n = self.N_INIT
                return self._fall_back.launch(S)    

class XWing(FmtParamSolvingMethod):
    N_THRESHOLD = 3
    N_INIT = 2
    _n = N_INIT

    def _find_option_in_n_by_n(self, S: Sudoku, n: int, primary_kind: str, option: int):
        primary_kind_tiles = []
        secondary_kind, = {"r", "c"}-{primary_kind}
        secondary_to_consider = []
        for counter in S.counters[primary_kind]:
            if len(tile_idxs:=counter[option-1]) == n:
                primary_kind_tiles.append(tile_idxs)
                secondary_pos = {S.tiles[idx].pos[secondary_kind] for idx in tile_idxs}
                secondary_to_consider.append(secondary_pos)
                if secondary_to_consider.count(secondary_pos) == n:
                    return [primary_kind_tiles[i] for i, scpos in enumerate(secondary_to_consider) if scpos==secondary_pos]

        return None
        
    def _option_in_n_by_n_removal(self, S: Sudoku, n: int, primary_kind: str, option: int):
        throw_away = set()
        secondary_kind, = {"r", "c"}-{primary_kind}
        if (primary_kind_tiles:=self._find_option_in_n_by_n(S, n, primary_kind, option)):
            found_tiles = {idx for idxs in primary_kind_tiles for idx in idxs}
   
            for tidx in primary_kind_tiles[0]:
                tile = S.tiles[tidx]
                secondary_kind_counter = S.counters[secondary_kind][tile.pos[secondary_kind]]
                secondary_kind_tiles = secondary_kind_counter[option-1]
                throw_away |= (secondary_kind_tiles - found_tiles)
            
            if len(throw_away) > 0:
                for tidx in throw_away:
                    self._stepper.set_consideration(
                        found_tiles,
                        {option},
                        f"found option {option} in {n}x{n} square at {found_tiles}, thus removing {option} from {tidx}",
                        True)

                    self._remove.launch(S, tidx, {option})
                    if S.violated:
                        return False

                return True

            else:
                return None     

    def launch(self, S: Sudoku):
        for direction in ("r", "c"):
            for option in range(1, 10):
                if S.violated:
                    return False

                if self._option_in_n_by_n_removal(S, self._n, direction, option):
                    # logging.info(f"{option} appears in {scale}x{scale} square")
                    self._n = self.N_INIT
                    return self._advance.launch(S)

        if self._n < self.N_THRESHOLD:
            self._n += 1
            return self.launch(S)
        else:
            self._n = self.N_INIT
            return self._fall_back.launch(S)

class YWing(FmtSolvingMethod):
    def _get_node_candidates(self, S: Sudoku, anchor: Tile):
        candidates = set()
        for kind in CONTAINER_TYPES:
            for tidx in S.containers[kind][anchor.pos[kind]]:
                tile = S.tiles[tidx]
                if (tile.n_options==2) and (len(tile.options&anchor.options) == 1):
                    candidates.add(tidx)

        candidates = list(candidates)
        # print(f"found canditates with options: {[c.options for c in candidates]} anchor has {anchor.options}")
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
        for anchor in filter(lambda idx: S.tiles[idx].n_options==2, range(81)):
            if S.violated:
                return False
            
            if self._find_y_wing_and_remove(S, anchor):
                return self._advance.launch(S)
        
        return self._fall_back.launch(S)

class Bifurcation(FmtSolvingMethod):
    def launch(self, S: Sudoku):
        for tile_index in range(81):
            tile = S.tiles[tile_index]
            if tile.n_options == 2:
                # logging.info(f"initiate bifurcation...")

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

