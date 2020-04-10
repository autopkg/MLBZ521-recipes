#!/usr/bin/env python
#
# StringRightSplitter.py Copyright 2020 by Zack Thompson (MLBZ521)
#
# Inspired by VersionSplitter.py from Elliot Jordan
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

__all__ = ["StringRightSplitter"]


class StringRightSplitter(Processor):

    """This processor splits a string starting from the right.
    Uses the "rsplit()" function.

    The processor will verify that the occurrence and index input variables
    are integers and if not, set them as integers.
    
    This was done since most people use key/string pairs and not key/integers.
    """

    input_variables = {
        "string_to_split": {
            "required": True,
            "description": "The version string that needs splitting."
        },
        "split_on": {
            "required": False,
            "description": "The character(s) to use for splitting the string."
            "(Defaults to a space.)"
        },
        "occurrence": {
            "required": False,
            "description": "The occurrence, from the right, to split on."
            "returned. (Defaults to 1.)"
        },
        "index": {
            "required": False,
            "description": "The desired index to return from the split string."
            "(Defaults to 0.)"
        },
        "return_variable": {
            "required": True,
            "description": "The desired variable name to assign the value to."
        }
    }
    output_variables = {
    }

    description = __doc__

    def main(self):

        string_to_split = self.env["string_to_split"]
        split_on = self.env.get("split_on", " ")
        occurrence = self.env.get("occurrence", 1)
        index = self.env.get("index", 0)
        return_variable = self.env["return_variable"]

        # Check if the index and occurrence values passed are an integer, if not set them to the integer type
        if isinstance(index, int) == False:
            index = int(index)
        if isinstance(occurrence, int) == False:
            occurrence = int(occurrence)

        desired_string = string_to_split.rsplit(split_on, occurrence)[index]

        self.output("Result:  {}".format(desired_string))
        self.env[return_variable] = desired_string

if __name__ == "__main__":
    processor = StringRightSplitter()
    processor.execute_shell()
