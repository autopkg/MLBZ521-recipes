#!/usr/bin/env python
#
# Copyright 2019 Zack T (mlbz521)
# Borrowed some of the dmg mount logic for included autopkg recipes.
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

import re
import os.path
from autopkglib.DmgMounter import DmgMounter
from autopkglib import Processor, ProcessorError

__all__ = ["TextFileReader"]

class TextFileReader(DmgMounter):

    """This processor finds the URL for the desired version, localization, and type of ARCHICAD.
    """

    input_variables = {
        "source": {
            "required": True,
            "description": "Source of the text file.  "
            "Can point to a path inside a .dmg which will be mounted.",
        },
        "file_to_open": {
            "required": True,
            "description": "The text file that needs to be opened for reading.",
        },
        "pattern": {
            "required": True,
            "description": "The regex pattern to look for and return.",
        }
    }
    output_variables = {
        "match": {
            "description": "Returns the rest of the line that matched the pattern."
        }
    }

    description = __doc__

    def main(self):

        # Define variables
        source = self.env.get('source')
        file_to_open = self.env.get('file_to_open')
        pattern = self.env.get('pattern')

        # Check if we're trying to copy something inside a dmg.
        (dmg_path, dmg, dmg_source_path) = self.parsePathForDMG(self.env['source'])

        try:
            # Mount dmg and copy path inside.
            mount_point = self.mount(dmg_path)

            # Wrap all other actions in a try/finally so the image is always unmounted.
            try:            
                # Open, read, and close file
                file = open(os.path.join(mount_point, file_to_open), 'r')
                contents = file.read()
                file.close()

                # Look for a match
                line = re.search(pattern + r'.*', contents)
                match = re.split(pattern, line.group())[1]

                if match:
                    self.env["match"] = match
                    self.output("match: {}".format(self.env["match"]))

            except BaseException as err:
                raise ProcessorError("Unable to find a match based on the parameters provided.")

            finally:
                self.unmount(dmg_path)

        except BaseException as err:
            raise ProcessorError("Unable to find a dmg, error: %s" % err)

if __name__ == "__main__":
    processor = TextFileReader()
    processor.execute_shell()
