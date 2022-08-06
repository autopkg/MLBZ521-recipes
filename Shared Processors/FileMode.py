#!/usr/local/autopkg/python
#
# Copyright 2022 Zack Thompson (MLBZ521)
#
# Copyright 2011 Per Olofsson
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

import os

from autopkglib import Processor, ProcessorError


__all__ = ["FileMode"]


class FileMode(Processor):
    """This processor essentially runs `chmod` on a file.
    Provide the numeric mode for file in octal format.
    """

    description = __doc__
    input_variables = {
        "file_path": {
            "required": True,
            "description": "Path to the file.",
        },
        "file_mode": {
            "required": True,
            "description": "Numeric mode for file in octal format."
        }
    }
    output_variables = {}


    def main(self):

        file_path = self.env["file_path"]
        file_mode = self.env["file_mode"]

        if not os.path.exists(self.env["file_path"]):
            raise ProcessorError(f"File does not exist:  {file_path}")

        try:
            os.chmod(file_path, int(file_mode, 8))
            self.output(f"Changed permissions to {file_mode} on {file_path}")

        except Exception as error:
            raise ProcessorError(f"Can't set mode of {file_path} to {file_mode}: {error}") from error


if __name__ == "__main__":
    PROCESSOR = FileMode()
    PROCESSOR.execute_shell()
