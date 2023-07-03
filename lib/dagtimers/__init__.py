# dagtimers : Nicely displayed timers.
# Copyright (C) 2023  Michael P. Lane
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import math
from contextlib import contextmanager
from time import time

__all__ = ["Timers"]

_START_TIME_DEFAULT = -1
_UNACCOUNTED_STR = "<Unaccounted>"
_EXCESS_STR = "<Excess>"

class Timers:

    def __init__(self):

        self._starts = {}
        self._dag = {}
        self._excess = 0
        self._path = [self._dag]
        self._parents = []

    @contextmanager
    def time(self, timer_name):

        try:
            self.start(timer_name)
            yield

        finally:
            self.stop()

    def start(self, timer_name):

        excess_start_time = time()

        try:
            _, elapsed, next_node_in_path = self._path[-1][timer_name]

        except KeyError:

            next_node_in_path = {}
            self._path[-1][timer_name] = (time(), 0, next_node_in_path)

        else:
            self._path[-1][timer_name] = (time(), elapsed, next_node_in_path)

        self._path.append(next_node_in_path)
        self._parents.append(timer_name)
        self._excess += time() - excess_start_time

    def stop(self):

        excess_start_time = time()
        timer_name = self._parents[-1]
        del self._path[-1]
        start_time, elapsed, dag = self._path[-1][timer_name]
        self._path[-1][timer_name] = (_START_TIME_DEFAULT, elapsed + time() - start_time, dag)
        self._excess += time() - excess_start_time
        del self._parents[-1]

    def _pretty_print(self, indent, root, parent_timer_name, parent):

        ret = ""

        if len(root) == 0:
            return ret

        has_parent = parent_timer_name is not None
        ordered = sorted(
            [timer_name for timer_name in root.keys() if root[timer_name][0] == _START_TIME_DEFAULT],
            key = lambda timer_name: -root[timer_name][1]
        )
        ordered.extend([timer_name for timer_name in root.keys() if root[timer_name][0] != _START_TIME_DEFAULT])
        accounted = sum(t[1] for t in root.values())

        if len(root) > 0:
            max_num_chars = max(len(timer_name) for timer_name in root.keys())

        else:
            max_num_chars = 0

        if has_parent:

            max_num_chars = max(max_num_chars, len(_UNACCOUNTED_STR))
            parent_running = parent[parent_timer_name][0] != _START_TIME_DEFAULT

            if not parent_running:

                parent_elapsed = parent[parent_timer_name][1]
                unaccounted = parent_elapsed - accounted

                if parent_elapsed != 0:
                    prop = (unaccounted / parent_elapsed) * 100

                else:
                    prop = 100

                if parent_elapsed != 0:

                    ret += "\t" * indent + f"<Unaccounted> : {unaccounted:.7f} ({prop:.3f}%)"

                    if self._excess != 0:
                        ret += f" [{math.floor(math.log10(parent_elapsed / self._excess))}]"

                    else:
                        ret += " [inf]"

                    ret += "\n"

        else:

            max_num_chars = max(max_num_chars, len(_EXCESS_STR))
            parent_elapsed = accounted
            parent_running = False

        for timer_name in ordered:

            elapsed = root[timer_name][1]
            running = root[timer_name][0] != _START_TIME_DEFAULT
            ret += "\t" * indent + f"{timer_name: <{max_num_chars}}"

            if not running:

                ret += f" : {elapsed:.7f}"

                if has_parent and not parent_running:

                    if parent_elapsed != 0:
                        prop = (elapsed / parent_elapsed) * 100

                    else:
                        prop = 100

                    ret += f" ({prop:.3f}%)"

                if self._excess != 0 and elapsed != 0:
                    ret += f" [{math.floor(math.log10(elapsed / self._excess))}]"

                else:
                    ret += f" [inf]"

                ret += "\n"

            else:
                ret += " : RUNNING\n"

            if len(root[timer_name][2]) > 0:
                ret += self._pretty_print(indent + 1, root[timer_name][2], timer_name, root)

        return ret

    def pretty_print(self):

        start_time = time()
        ret = self._pretty_print(0, self._dag, None, None)

        if len(self._dag) > 0:
            max_num_chars = max(len(timer_name) for timer_name in self._dag.keys())

        else:
            max_num_chars = 0

        max_num_chars = max(max_num_chars, len(_EXCESS_STR))
        self._excess += time() - start_time
        return f"{_EXCESS_STR: <{max_num_chars}} : {self._excess:.7f}\n" + ret
