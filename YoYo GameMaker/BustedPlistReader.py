#!/usr/local/autopkg/python
#
# Copyright 2022 Zack Thompson (MLBZ521)
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

"""See docstring for BustedPlistReader class"""

import os.path
import re

from autopkglib import ProcessorError, Processor


__all__ = ["BustedPlistReader"]


class BustedPlistReader(Processor):
    """This processor reads a text file and looks for a regex pattern and 
    returns the rest of the line that matched the pattern.
    """

    description = __doc__
    input_variables = {
        "source_path": {
            "required": True,
            "description": "Path to the text file that needs to be read.  "
            "Can point to a path inside a .dmg which will be mounted."
        },
        "pattern": {
            "required": True,
            "description": "The regex pattern to look for and return."
        }
    }
    output_variables = {
        "version": {
            "description": "Returns the version."
        }
    }


    def main(self):

        # Define variables
        source_path = os.path.normpath(self.env["source_path"])
        pattern = self.env.get('pattern')

        try:
            with open(source_path, 'rb') as file:
                contents = file.read().split(b"bplist")[0].decode()

        except Exception as error:
            raise ProcessorError(f"Unable to open '{source_path}'") from error

        try:
            # Look for a match
            line = re.search(pattern, contents)
            match = re.search("<string>(.+)</string>", line.group()).groups()[0]

            self.env["version"] = match
            self.output(f"version: {self.env['version']}")

        except Exception as error:
            raise ProcessorError("Unable to find a match based on the pattern provided.") from error


if __name__ == "__main__":
    PROCESSOR = BustedPlistReader()
    PROCESSOR.execute_shell()
