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

import plistlib

from autopkglib import Processor, ProcessorError


__all__ = ["JVMVersioner"]


class JVMVersioner(Processor):
    """This processor finds the Java Virtual Machine version in a JDK package.
    """

    description = __doc__
    input_variables = {
        "plist": {
            "required": True,
            "description": "The plist file that will be searched.",
        }
    }
    output_variables = {
        "jvm_version": {
            "description": "Returns the JVM version found."
        }
    }


    def main(self):

        # Define the plist file.
        plist = self.env.get("plist")

        try:
            with open(plist, "rb") as file:
                plist_contents = plistlib.load(file)
        except Exception as error:
            raise ProcessorError("Unable to load the specified plist file.") from error

        # Get the latest version.
        jvm_version=plist_contents.get("JavaVM").get("JVMVersion")

        if jvm_version:
            # self.env["jvm_version"] = jvm_version
            self.env["version"] = jvm_version
            self.output(f"jvm_version: {self.env['version']}")
        else:
            raise ProcessorError("Unable to determine the Java Virtual Machine version.")


if __name__ == "__main__":
    PROCESSOR = JVMVersioner()
    PROCESSOR.execute_shell()
