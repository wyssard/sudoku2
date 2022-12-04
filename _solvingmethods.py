from __future__ import annotations

from sudoku import Sudoku, CONTAINER_TYPES
from _formatting import STEPPERS, Stepper

from typing import Set, List, Callable
from copy import deepcopy
import logging


class FmtSolvingBase:
    def __init__(self, formatting: str, stepping: bool) -> None:
        self._stepper: Stepper = STEPPERS[stepping](formatting)

    def launch(self, S: Sudoku, *args):
        pass

class FmtSolvingMethod(FmtSolvingBase):
    def __init__(self, formatting: str, stepping: bool, fall_back: FmtSolvingMethod, advance: FmtSolvingMethod|None) -> None:
        super().__init__(formatting, stepping)
        self._advance = advance if advance else self
        self._fall_back = fall_back

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

                    self._stepper.considered_tiles = {where_only_one_left}
                    self._stepper.considered_options = {o}

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

    def _get_equivalent_tiles(self, S: Sudoku, where: Set[int], tile_index: int) -> Set[int]:
        """
        return indices of all tiles within `where` that have the same options 
        as the tile at `which` 
        (`which` is also included)
        """
        
        if (tile:=S.tiles[tile_index]).n_options == 1:
            # print(f"tile {tile_index} has only one option")
            return {tile_index}

        else:
            matches = set()
            for tile_index in where:
                if S.tiles[tile_index].options == tile.options:
                    matches.add(tile_index)
            # print(f"found {len(matches)} equiv tile anyways")
            return matches if len(matches)==tile.n_options else set()

    def _n_times_n_options_removal_container(self, S: Sudoku, kind: str, container_index: int, n: int) -> bool:
        success = False
        container = S.containers[kind][container_index]
        
        for tile_index in container:
            if len(matches:=self._get_equivalent_tiles(S, container, tile_index)) == n:
                
                self._stepper.considered_tiles = matches
                self._stepper.considered_options = S.tiles[tile_index].options

                for unmatched in set(container)-matches:
                    if self.remove_options(S, unmatched, S.tiles[tile_index].options):
                        success = True
                        print(f"std n={n} removal")
                    if S.violated:
                        return False

        return success

    def launch(self, S: Sudoku):
        if S.done:
            self._stepper.show(S)
            return S
        else:
            for kind in CONTAINER_TYPES:
                for kind_index in range(9):
                    if S.violated:
                        return False

                    if self._n_times_n_options_removal_container(S, kind, kind_index, self._n):
                        # logging.info(f"{n} numbers in {n} tiles reduction")
                        self._n = self.N_INIT
                        return self._advance.launch(S)

            if self._n < self.N_THRESHOLD:
                self._n += 1
                return self.launch(S)
            else:
                self._n = self.N_INIT
                return self._fall_back.launch(S)    


class XWing(FmtSolvingMethod):
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
            # print(f"trying {n} x {n} removal with option {option} considering {found_tiles}")
            for tidx in primary_kind_tiles[0]:
                tile = S.tiles[tidx]
                secondary_kind_counter = S.counters[secondary_kind][tile.pos[secondary_kind]]
                secondary_kind_tiles = secondary_kind_counter[option-1]
                throw_away |= (secondary_kind_tiles - found_tiles)
            
            if len(throw_away) > 0:
                
                self._stepper.considered_tiles = found_tiles
                self._stepper.considered_options = {option}

                # self._stepper(S, found_tiles, {option}, throw_away, {option})

                for tidx in throw_away:
                    self.remove_options(S, tidx, {option})
                    logging.info(f"{n}x{n} removal at {tidx}")
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

class Bifurcation(FmtSolvingMethod):
    def launch(self, S: Sudoku):
        for tile_index in range(81):
            tile = S.tiles[tile_index]
            if tile.n_options == 2:
                # logging.info(f"initiate bifurcation...")

                opts = deepcopy(tile.options)
                
                backup = deepcopy(S)
                try_option = opts.pop()
                
                self.remove_options(backup, tile_index, {try_option})
                if not (out:=self.n_times_n_options_removal(backup, 1)):
                    backup = deepcopy(S)
                    self.remove_options(backup, tile_index, {opts.pop()})
                    out = self.n_times_n_options_removal(backup, 1)

                # logging.info(f"exit bifurcation")
                return out


class _FormattedSolving:
    def __init__(self, formatting: str, stepping: False) -> None:
        self._stepper: Stepper = STEPPERS[stepping](formatting)

    def load_content(self, S: Sudoku, content: List[int]):
        occupied_tiles = []
        for tile_index in range(81):
            tile = S.tiles[tile_index]
            if val:=content[tile_index]:
                tile.options = {val}
                occupied_tiles.append((tile_index, val))

            S.tiles.append(tile)
            for kind in CONTAINER_TYPES:
                S.containers[kind][tile.pos[kind]].append(tile_index)

                counter = S.counters[kind][tile.pos[kind]]
                for o in tile.options:
                    counter[o-1].add(tile_index)

        for kind in CONTAINER_TYPES:
            for idx in range(9):
                self._n_times_n_options_removal_container(S, kind, idx, 1)
        
        return S


    

