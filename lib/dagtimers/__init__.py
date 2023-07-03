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

__all__ = ["Timers", "TimerError"]

_START_TIME_DEFAULT = -1
_UNACCOUNTED_STR = "<Unaccounted>"
_EXCESS_STR = "<Excess>"
_INDENT = "    |"
_START_TIME_INDEX = 0
_ELAPSED_INDEX = 1
_CHILDREN_INDEX = 2
_NUM_STARTS_INDEX = 3

class TimerError(RuntimeError): pass

class Timers:

    def __init__(self):

        self._starts = {}
        self._num_start = 0
        self._dag = {}
        self._excess = 0
        self._path = [self._dag]
        self._parents = []
        self._last_pretty_print_time = _START_TIME_DEFAULT

    def time_iter(self, timer_name, iter_):

        started = False

        try:

            self.start(timer_name)
            started = True

            for item in iter_:

                self.stop()
                started = False
                yield item
                self.start(timer_name)
                started = True

            self.stop()
            started = False

        finally:

            if started:
                self.stop()

    @contextmanager
    def time_cm(self, timer_name, cm):

        started = False

        try:

            self.start(timer_name)
            started = True

            with cm as yield_:

                self.stop()
                started = False
                yield yield_
                self.start(timer_name)
                started = True

            self.stop()
            started = False

        finally:

            if started:
                self.stop()

    @contextmanager
    def time(self, timer_name):

        try:
            self.start(timer_name)
            yield

        finally:
            self.stop()

    def start(self, timer_name):

        excess_start_time = time()
        self._num_start += 1

        try:
            _, elapsed, next_node_in_path, num_starts = self._path[-1][timer_name]

        except KeyError:

            next_node_in_path = {}
            self._path[-1][timer_name] = (time(), 0, next_node_in_path, 1)

        else:
            self._path[-1][timer_name] = (time(), elapsed, next_node_in_path, num_starts + 1)

        self._path.append(next_node_in_path)
        self._parents.append(timer_name)
        self._excess += time() - excess_start_time

    def stop(self):

        excess_start_time = time()

        if len(self._parents) == 0:
            raise TimerError("No timers currently running.")

        timer_name = self._parents[-1]
        del self._path[-1]
        start_time, elapsed, dag, num_starts = self._path[-1][timer_name]
        self._path[-1][timer_name] = (_START_TIME_DEFAULT, elapsed + time() - start_time, dag, num_starts)
        self._excess += time() - excess_start_time
        del self._parents[-1]

    def _pretty_print(self, indent, root, parent_timer_name, parent):

        ret = ""

        if len(root) == 0:
            return ret

        has_parent = parent_timer_name is not None
        ordered = sorted(
            [timer_name for timer_name in root.keys() if root[timer_name][_START_TIME_INDEX] == _START_TIME_DEFAULT],
            key = lambda timer_name: -root[timer_name][_ELAPSED_INDEX]
        )
        ordered.extend(
            [timer_name for timer_name in root.keys() if root[timer_name][_START_TIME_INDEX] != _START_TIME_DEFAULT]
        )
        accounted = sum(t[_ELAPSED_INDEX] for t in root.values())
        max_num_chars = max(len(timer_name) for timer_name in root.keys())

        if has_parent:

            max_num_chars = max(max_num_chars, len(_UNACCOUNTED_STR))
            parent_running = parent[parent_timer_name][0] != _START_TIME_DEFAULT

            if not parent_running:

                parent_elapsed = parent[parent_timer_name][_ELAPSED_INDEX]
                unaccounted = parent_elapsed - accounted

                if parent_elapsed != 0:
                    prop = (unaccounted / parent_elapsed) * 100

                else:
                    prop = 100

                if parent_elapsed != 0:
                    ret += _INDENT * indent + f"<Unaccounted> : {unaccounted:.7f} ({prop:.3f}%)\n"

        else:

            max_num_chars = max(max_num_chars, len(_EXCESS_STR))
            parent_elapsed = accounted
            parent_running = False

        for timer_name in ordered:

            elapsed = root[timer_name][_ELAPSED_INDEX]
            running = root[timer_name][_START_TIME_INDEX] != _START_TIME_DEFAULT
            ret += _INDENT * indent + f"{timer_name: <{max_num_chars}}"

            if not running:

                ret += f" : {elapsed:.7f}"

                if has_parent and not parent_running:

                    if parent_elapsed != 0:
                        prop = (elapsed / parent_elapsed) * 100

                    else:
                        prop = 100

                    ret += f" ({prop:.3f}%)"

                if self._excess != 0 and elapsed != 0:

                    inside_log = self._num_start * elapsed / (self._excess * root[timer_name][_NUM_STARTS_INDEX])
                    ret += f" [{math.floor(math.log10(inside_log))}]"

                else:
                    ret += f" [inf]"

                ret += "\n"

            else:
                ret += " : RUNNING\n"

            if len(root[timer_name][2]) > 0:
                ret += self._pretty_print(indent + 1, root[timer_name][2], timer_name, root)

        return ret

    def pretty_print(self):

        ret = self._pretty_print(0, self._dag, None, None)

        if len(self._dag) > 0:
            max_num_chars = max(len(timer_name) for timer_name in self._dag.keys())

        else:
            max_num_chars = 0

        max_num_chars = max(max_num_chars, len(_EXCESS_STR))
        return f"{_EXCESS_STR: <{max_num_chars}} : {self._excess:.7f}\n" + ret
