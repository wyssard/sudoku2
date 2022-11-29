from __future__ import annotations

from sudoku import Sudoku, CONTAINER_TYPES
from _formatting import STEPPERS, _Stepper

from csv import reader
from pathlib import Path
from typing import Set, List
from copy import deepcopy
import logging

        
class _FormattedSolving:
    def __init__(self, formatting: str, stepping: False) -> None:
        self._stepper: _Stepper = STEPPERS[stepping](formatting)

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

                    if not self.remove_options(S, where_only_one_left, remove_opts):
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
        

    def remove_options(self, S: Sudoku, where: int, which: set) -> bool:
        tile = S.tiles[where]
        if (diff:=tile.options & which):
            
            self._stepper.show_step(S, {where}, which)

            tile.options -= which
            if tile.n_options > 0:
                return self._update_counter(S, where, diff)
                
        else:
            return False
    
    def add_options(self, where: int, which: set) -> None:
        """
        future method artificially construct specific situations; useful in 
        particular when testing solving rules
        """
        pass
                


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

    def n_times_n_options_removal(self, S: Sudoku, n: int):
        if S.done:
            self._stepper.show(S)
            return S
        else:
            for kind in CONTAINER_TYPES:
                for kind_index in range(9):
                    if S.violated:
                        return False

                    if self._n_times_n_options_removal_container(S, kind, kind_index, n):
                        # logging.info(f"{n} numbers in {n} tiles reduction")
                        return self.n_times_n_options_removal(S, 1)

            if n < 3:
                return self.n_times_n_options_removal(S, n+1)
            else:
                return self.n_by_n_removal(S, 2)
    


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

    def n_by_n_removal(self, S: Sudoku, scale: int):
        for direction in ("r", "c"):
            for option in range(1, 10):
                if S.violated:
                    return False

                if self._option_in_n_by_n_removal(S, scale, direction, option):
                    # logging.info(f"{option} appears in {scale}x{scale} square")
                    return self.n_times_n_options_removal(S, 1)

        if scale < 3:
            return self.n_by_n_removal(S, scale+1)
        else:
            return self.auto_try(S)



    def auto_try(self, S: Sudoku):
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


def solve(path: Path, formatting: str, stepping: bool) -> Sudoku:
    fmtsol = _FormattedSolving(formatting, stepping)

    with open(path) as csvfile:
        rows = reader(csvfile, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    sudoku = fmtsol.load_content(Sudoku(), content)

    return fmtsol.n_times_n_options_removal(sudoku, 1)

def load(path: Path) -> Sudoku:
    with open(path) as csvfile:
        rows = reader(csvfile, skipinitialspace=True)
        content = [(int(elt) if elt else 0) for row in rows for elt in row]

    return Sudoku(content)

def save(sudoku: Sudoku, dest: Path):
    pass

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    s = solve("examples/evil2.csv", "grid", False)
    # print(s)
    