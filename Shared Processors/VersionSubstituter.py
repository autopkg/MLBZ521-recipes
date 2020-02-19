#!/usr/bin/env python
#
# Original:  VersionSplitter.py
# Copyright 2015 Elliot Jordan
#
# VersionSubstituter.py
# Modified 2018 by Zack Thompson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

from autopkglib import Processor, ProcessorError

__all__ = ["VersionSubstituter"]


class VersionSubstituter(Processor):

    """This processor substitutes character(s) in a string by number of occurrences.
    By default, it splits using a dash only the first item.
    Default behavior example: "3.0.8-2" --> "3.0.8b2"
    """

    input_variables = {
        "version": {
            "required": True,
            "description": "The version string that needs to be edited."
        },
        "old": {
            "required": False,
            "description": "The old character(s) to be replaced in the "
                           "version string. (Defaults to a dash.)"
        },
        "new": {
            "required": True,
            "description": "The new character(s) that will replace the "
                           "old version string."
        },
        "index": {
            "required": False,
            "description": "The the max number of occurrences to replace "
                           "the old character(s). (Defaults to 1.)"
        }
    }
    output_variables = {
        "version": {
            "description": "The cleaned up version string."
        }
    }
    description = __doc__

    def main(self):

        old = self.env.get("old", "-")
        new = self.env.get("new")
        index = self.env.get("index", 1)
        self.env["version"] = self.env["version"].replace(old, new, index)
        self.output("Substitute version: {}".format(self.env["version"]))


if __name__ == "__main__":
    processor = VersionSubstituter()
    processor.execute_shell()
