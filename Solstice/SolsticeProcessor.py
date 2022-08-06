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
import shutil
import subprocess
import time

from autopkglib import Processor, ProcessorError
from SystemConfiguration import SCDynamicStoreCopyConsoleUser


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


    def main(self):

        def runUtility(command):
            """A helper function for subprocess.
            Args:
                command:  List containing command and arguments in a list
            Returns:
                stdout:  output of the command
            """
            try:
                process = subprocess.Popen(command)

            except subprocess.CalledProcessError as error:
                self.output(f"return code = {error.returncode}")
                self.output(f"result = {error}")

            return process


        # Define some variables.
        bootstrapper_location = self.env.get("bootstrapper_location")
        move_to = self.env.get("move_to")
        time_counter = 0

        # The final .app is saved to the logged in users home directory, so we get that.
        username = (SCDynamicStoreCopyConsoleUser(None, None, None) or [None])[0]
        username = [username,""][username in [u"loginwindow", None, u""]]

        # Run the binary to build the final .app.
        bootstrapper = [f"{bootstrapper_location}/Contents/MacOS/SolsticeClientInstallerMac"]
        build = runUtility(bootstrapper)

        # Give it eight seconds to build the app, and then kill the process -- we don't want the app launching.
        while not os.path.exists(f"/Users/{username}/Desktop/Mersive Solstice.app/Contents/Info.plist"):

            # This method was proposed by @dcoobs (github.com/dcoobs)
            time.sleep(1)
            time_counter += 1

            if time_counter > 8:
                break

        build.kill()

        if os.path.exists(f"/Users/{username}/Desktop/Mersive Solstice.app"):

            # Move the file from the home directory, back into the Autopkg Cache directory.
            shutil.move(f"/Users/{username}/Desktop/Mersive Solstice.app", f"{move_to}/Mersive Solstice.app")

        else:
            raise ProcessorError("The Mersive Solstice.app wasn't at the expected location.")

        # Define the plist file.
        plist = f"{move_to}/Mersive Solstice.app/Contents/Info.plist"

        # Get the contents of the plist file.
        try:
            with open(plist, "rb") as file:
                plist_contents = plistlib.load(file)

        except Exception:
            raise ProcessorError("Unable to locate the specified plist file.")

        # Get the version and bundle id
        version=plist_contents.get("CFBundleShortVersionString")
        bundle_id=plist_contents.get("CFBundleIdentifier")

        # Output
        self.env["version"] = version
        self.output(f"Version: {self.env['version']}")
        self.env["bundle_id"] = bundle_id
        self.output(f"Bundle Identifier: {self.env['bundle_id']}")


if __name__ == "__main__":
    PROCESSOR = SolsticeProcessor()
    PROCESSOR.execute_shell()
