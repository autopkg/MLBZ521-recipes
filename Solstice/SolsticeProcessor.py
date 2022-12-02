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

import os
import plistlib
import re
import shutil
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["SolsticeProcessor"]


class SolsticeProcessor(Processor):

    """This processor uses the extracted "bootstrapper".app to build the final .app as well as grab
    some additional information for building the package.
    """

    description = __doc__
    input_variables = {
        "bootstrapper_location": {
            "required": True,
            "description": "The location of the extracted .app that builds the final .app.",
        },
        "move_to": {
            "required": True,
            "description": "The Autopkg Cache directory for this recipe.",
        }
    }
    output_variables = {
        "bundle_id": {
            "description": "Returns the bundle_id to use to build the package."
        },
        "version": {
            "description": "Returns the .app's version."
        }
    }


    def get_console_user(self):

        # Get the Console User
        results_console_user = self.execute_process(
            "/usr/sbin/scutil", "show State:/Users/ConsoleUser")
        return re.sub(
            "(Name : )|(\n)", "", ( re.search("Name : .*\n", results_console_user["stdout"])[0] ))


    def execute_process(self, command, input=None):
        """
        A helper function for subprocess.

        Args:
            command (str):  The command line level syntax that would be
                written in shell or a terminal window.
        Returns:
            Results in a dictionary.
        """

        # Validate that command is not a string
        if not isinstance(command, str):
            raise TypeError('Command must be a str type')

        # Format the command
        # command = shlex.quote(command)

        # Run the command
        process = subprocess.Popen(
            command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        if input:
            (stdout, stderr) = process.communicate(input=bytes(input, "utf-8"))
        else:
            (stdout, stderr) = process.communicate()

        return {
            "stdout": (stdout.decode()).strip(),
            "stderr": (stderr.decode()).strip() if stderr != None else None,
            "status": process.returncode,
            "success": True if process.returncode == 0 else False,
            "process": process
        }


    def main(self):

        bootstrapper_location = self.env.get("bootstrapper_location")
        move_to = self.env.get("move_to")

        # The final .app is saved to the logged in users home directory.
        username = self.get_console_user()

        # Run the binary to build the final .app.
        bootstrapper = f"{bootstrapper_location}/Contents/MacOS/SolsticeClientInstallerMac"
        build = self.execute_process(bootstrapper)
        build.get("process").kill()

        if os.path.exists(f"/Users/{username}/Desktop/Mersive Solstice.app"):

            # Move the file from the home directory, back into the Autopkg Cache directory.
            shutil.move(
                f"/Users/{username}/Desktop/Mersive Solstice.app", 
                f"{move_to}/Mersive Solstice.app"
            )

        else:
            raise ProcessorError("The Mersive Solstice.app wasn't at the expected location.")

        # Get the contents of the plist file.
        try:
            plist = f"{move_to}/Mersive Solstice.app/Contents/Info.plist"
            with open(plist, "rb") as file:
                plist_contents = plistlib.load(file)

        except Exception as error:
            raise ProcessorError("Unable to locate the specified plist file.") from error

        # Get the version and bundle id
        version=plist_contents.get("CFBundleShortVersionString")
        bundle_id=plist_contents.get("CFBundleIdentifier")
        self.env["version"] = version
        self.output(f"Version: {self.env['version']}")
        self.env["bundle_id"] = bundle_id
        self.output(f"Bundle Identifier: {self.env['bundle_id']}")


if __name__ == "__main__":
    PROCESSOR = SolsticeProcessor()
    PROCESSOR.execute_shell()
