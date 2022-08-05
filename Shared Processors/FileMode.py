#!/usr/local/autopkg/python
#
# Copyright 2011 Per Olofsson
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

import os

from autopkglib import Processor, ProcessorError

__all__ = ["FileMode"]

class FileMode(Processor):

    """This processor essentinally runs `chmod` on a file.
    Provide the numeric mode for file in octal format
    """

    description = __doc__
    input_variables = {
        "file_path": {
            "required": True,
            "description": "Path to the file.",
        },
        "file_mode": {
            "required": True,
            "description": "String. Numeric mode for file in octal format."
        }
    }
    output_variables = {
    }

    def main(self):
        if 'file_mode' in self.env:
            try:
                os.chmod(self.env['file_path'], int(self.env['file_mode'], 8))
                self.output("Set permissions on file at %s" % self.env['file_path'])
            except Exception as err:
                raise ProcessorError(
                    "Can't set mode of %s to %s: %s"
                    % (self.env['file_path'], self.env['file_mode'], err))

if __name__ == '__main__':
    PROCESSOR = FileMode()
    PROCESSOR.execute_shell()
