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

from setuptools import setup

setup(
    name = 'dagtimers',
    version = "0.1",
    description = "Nicely displayed timers.",
    long_description = "Nicely displayed timers.",
    long_description_content_type="text/plain",
    author = "Michael P. Lane",
    author_email = "mlanetheta@gmail.com",
    url = "https://github.com/automorphis/dagtimers",
    package_dir = {"": "lib"},
    packages = [
        "dagtimers",
        "cornifer._utilities"
    ],
    zip_safe=False
)