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

        start_time = time()

        try:
            next_node_in_path = self._path[-1][timer_name][2]

        except KeyError:

            next_node_in_path = {}
            self._path[-1][timer_name] = (time(), 0, next_node_in_path)

        self._path.append(next_node_in_path)
        self._parents.append(timer_name)
        self._excess += time() - start_time

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
        ordered = sorted(root.keys(), key = lambda timer_name : -root[timer_name][1])
        accounted = sum(t[1] for t in root.values())
        max_num_chars = max(len(timer_name) for timer_name in root.keys())

        if has_parent:

            parent_running = parent[parent_timer_name][0] == _START_TIME_DEFAULT

            if not parent_running:
                parent_elapsed = parent[parent_timer_name][1]
                unaccounted = parent_elapsed - accounted
                prop = (unaccounted / parent_elapsed) * 100
                ret += "\t" * indent + f"Unaccounted : {unaccounted:.7f} ({prop:.3f}%)\n"

        else:

            parent_elapsed = accounted
            parent_running = False

        for timer_name in ordered:

            elapsed = root[timer_name][1]
            running = root[timer_name][0] == _START_TIME_DEFAULT
            ret += "\t" * indent + f"{timer_name: <{max_num_chars}}"

            if not running:

                ret += f" : {elapsed: .7f}"

                if not parent_running:

                    prop = (elapsed / parent_elapsed) * 100
                    ret += f" ({prop:.3f}%)\n"

                ret += f" [{math.floor(math.log10(elapsed / self._excess))}]"

            else:
                ret += " : RUNNING"

            if len(root[timer_name]) > 0:
                ret += self._pretty_print(indent + 1, root[timer_name][2], timer_name, root[timer_name][2])

        return ret

    def pretty_print(self):

        start_time = time()
        ret = self._pretty_print(0, self._dag, None, None)
        self._excess += time() - start_time
        return f"Excess : {self._excess:.7f}\n" + ret
