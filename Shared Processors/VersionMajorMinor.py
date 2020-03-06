#!/usr/bin/env python
#
# Original:  VersionSplitter.py
# Copyright 2015 Elliot Jordan
#
# VersionMajorMinor.py
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

import re

from autopkglib import Processor, ProcessorError

__all__ = ["VersionMajorMinor"]


class VersionMajorMinor(Processor):

    """This processor splits a version string into only the 'Major.Minor' numerals.
    Expected format is Semantic Versioning.
    Default behavior example: "3.6.5" --> "3.6"
    """

    input_variables = {
        "version": {
            "required": True,
            "description": "The version string that needs to be edited."
        },
    }
    output_variables = {
        "major_minor_version": {
            "description": "The cleaned up version string."
        }
    }
    description = __doc__

    def main(self):

        major_Minor_Version = re.search(r"\d[.]\d", self.env["version"])
        self.env["major_minor_Version"] = major_Minor_Version.group()
        self.output("Major.Minor Version: {}".format(self.env["major_minor_Version"]))

if __name__ == "__main__":
    processor = VersionMajorMinor()
    processor.execute_shell()
