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

from time import sleep
from unittest import TestCase
from dagtimers import Timers, _START_TIME_DEFAULT

class TestTimers(TestCase):

    def test_start(self):

        timers = Timers()
        timers.start("hello")
        self.assertIn(
            "hello",
            timers._dag.keys()
        )
        self._assert_node(timers._dag, "hello", False, True, 0.0, [])
        self._assert_path(timers, ["hello"])
        timers.start("hi")
        self._assert_node(
            timers._dag, "hello", False, True, 0.0, [
                (timers._dag["hello"][2], "hi", False, True, 0.0, [])
            ]
        )
        self._assert_path(timers, ["hello", "hi"])
        timers.start("sup")
        self._assert_node(
            timers._dag, "hello", False, True, 0.0, [
                (timers._dag["hello"][2], "hi", False, True, 0.0, [
                    (timers._dag["hello"][2]["hi"][2], "sup", False, True, 0.0, [])
                ])
            ]
        )
        self._assert_path(timers, ["hello", "hi", "sup"])

    def test_stop(self):

        timers = Timers()
        timers.start("hello")
        self._assert_node(timers._dag, "hello", False, True, 0.0, [])
        self._assert_path(timers, ["hello"])
        sleep(0.25)
        timers.stop()
        self._assert_node(timers._dag, "hello", True, False, 0.25, [])
        self._assert_path(timers, [])
        timers.start("hello")
        self._assert_node(timers._dag, "hello", False, False, 0.25, [])
        self._assert_path(timers, ["hello"])
        sleep(0.5)
        timers.stop()
        self._assert_node(timers._dag, "hello", True, False, 0.75, [])
        self._assert_path(timers, [])
        timers.start("hello")
        timers.start("hi")
        self._assert_node(timers._dag, "hello", False, False, 0.75, [
            (timers._dag["hello"][2], "hi", False, True, 0.0, [])
        ])
        self._assert_path(timers, ["hello", "hi"])
        sleep(0.1)
        timers.stop()
        self._assert_node(timers._dag, "hello", False, False, 0.75, [
            (timers._dag["hello"][2], "hi", True, False, 0.1, [])
        ])
        self._assert_path(timers, ["hello"])
        timers.start("hello")
        self._assert_node(timers._dag, "hello", False, False, 0.75, [
            (timers._dag["hello"][2], "hi", True, False, 0.1, []),
            (timers._dag["hello"][2], "hello", False, True, 0.0, [])
        ])
        self._assert_path(timers, ["hello", "hello"])
        sleep(0.2)
        timers.stop()
        self._assert_node(timers._dag, "hello", False, False, 0.75, [
            (timers._dag["hello"][2], "hi", True, False, 0.1, []),
            (timers._dag["hello"][2], "hello", True, False, 0.2, [])
        ])
        self._assert_path(timers, ["hello"])
        timers.stop()
        self._assert_node(timers._dag, "hello", True, False, 1.05, [
            (timers._dag["hello"][2], "hi", True, False, 0.1, []),
            (timers._dag["hello"][2], "hello", True, False, 0.2, [])
        ])
        self._assert_path(timers, [])

    def test_pretty_print(self):

        timers = Timers()
        self._assert_indent_profile(timers.pretty_print(), [0])
        timers.start("hi")
        self._assert_indent_profile(timers.pretty_print(), [0, 0])
        sleep(0.05)
        timers.stop()
        self._assert_indent_profile(timers.pretty_print(), [0, 0])
        timers.start("hi")
        self._assert_indent_profile(timers.pretty_print(), [0, 0])
        sleep(0.2)
        timers.stop()
        self._assert_indent_profile(timers.pretty_print(), [0, 0])
        timers.start("startyyyyy")
        self._assert_indent_profile(timers.pretty_print(), [0, 0, 0])
        sleep(0.1)
        timers.stop()
        self._assert_indent_profile(timers.pretty_print(), [0, 0, 0])
        timers.start("hi")
        sleep(0.01)
        self._assert_indent_profile(timers.pretty_print(), [0, 0, 0])
        timers.start("hello")
        sleep(0.01)
        self._assert_indent_profile(timers.pretty_print(), [0, 0, 0, 1])
        timers.stop()
        self._assert_indent_profile(timers.pretty_print(), [0, 0, 0, 1])
        timers.stop()
        self._assert_indent_profile(timers.pretty_print(), [0, 0, 1, 1, 0])



    def _assert_node(self, node, timer_name, default_start_time, zero_elasped, elapsed_lb, children):

        self.assertIn(
            timer_name,
            node.keys()
        )

        if default_start_time:
            self.assertEqual(
                node[timer_name][0],
                _START_TIME_DEFAULT
            )

        else:

            try:
                self.assertNotEqual(
                    node[timer_name][0],
                    _START_TIME_DEFAULT
                )

            except AssertionError:
                raise

        if zero_elasped:
            self.assertEqual(
                node[timer_name][1],
                0
            )

        else:

            try:
                self.assertNotEqual(
                    node[timer_name][1],
                    0
                )

            except AssertionError:
                raise

            self.assertGreaterEqual(
                node[timer_name][1],
                elapsed_lb
            )

        for child_args in children:
            self._assert_node(*child_args)

        self.assertEqual(
            len(node[timer_name][2]),
            len(children)
        )

    def _assert_path(self, timers, exp_path_names):

        self.assertEqual(
            timers._path[0],
            timers._dag
        )
        self.assertEqual(
            len(timers._path),
            len(exp_path_names) + 1
        )
        node = timers._dag

        for exp_path_name, path_node in zip(exp_path_names, timers._path[1:]):

            node = node[exp_path_name][2]
            self.assertEqual(
                node,
                path_node
            )

        self.assertEqual(
            timers._parents,
            exp_path_names
        )

    def _assert_indent_profile(self, pretty_print, profile):

        try:
            self.assertEqual(
                len(profile),
                pretty_print.count("\n")
            )

        except AssertionError:
            raise

        for level, line in zip(profile, pretty_print[:-1].split("\n")):

            self.assertEqual(
                line[:level],
                "\t" * level
            )
            self.assertNotEqual(
                line[level],
                "\t"
            )







