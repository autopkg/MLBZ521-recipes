#!/usr/bin/env python
#
# Copyright 2019 Zack T (mlbz521)
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
import shutil
import subprocess
import time
from autopkglib import Processor, ProcessorError
from SystemConfiguration import SCDynamicStoreCopyConsoleUser
try:
    from plistlib import load as plist_Reader  # For Python 3
except ImportError:
    from plistlib import readPlist as plist_Reader  # For Python 2


__all__ = ["SolsticeProcessor"]

class SolsticeProcessor(Processor):

    """This processor uses the extracted "bootstrapper".app to build the final .app as well as grab
    some addition information for building the package.
    """

    input_variables = {
        "bootstrapperLocation": {
            "required": True,
            "description": "The location of the extracted .app that builds the final .app.",
        },
        "moveTo": {
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

    description = __doc__

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
                print ('return code = ', error.returncode)
                print ('result = ', error)  

            return process

        # Define some variables.
        bootstrapperLocation = self.env.get("bootstrapperLocation")
        moveTo = self.env.get("moveTo")

        # Run the binary to build the final .app.
        bootstrapper = ['{}/Contents/MacOS/SolsticeClientInstallerMac'.format(bootstrapperLocation)]
        build = runUtility(bootstrapper)
        
        # Give it five seconds to build the app, and then kill the process -- we don't want the app launching.
        time.sleep(5)
        build.kill()

        # The final .app is saved to the logged in users home directory, so we get that.
        username = (SCDynamicStoreCopyConsoleUser(None, None, None) or [None])[0]
        username = [username,""][username in [u"loginwindow", None, u""]]

        if os.path.exists("/Users/{}/Desktop/Solstice Client.app".format(username)):
            # Move the file from the home directory, back into the Autopkg Cache directory.
            shutil.move("/Users/{}/Desktop/Solstice Client.app".format(username), "{}/Solstice Client.app".format(moveTo))
        else:
            raise ProcessorError("The Solstice Client.app wasn't at the expected location.")

        # Define the plist file.
        plist = "{}/Solstice Client.app/Contents/Info.plist".format(moveTo)

        # Get the contents of the plist file.
        try:
            plist_contents = plist_Reader(plist)
        except Exception:
            raise ProcessorError('Unable to locate the specified plist file.')

        # Get the version and bundle id
        version=plist_contents.get('CFBundleShortVersionString')
        bundle_id=plist_contents.get('CFBundleIdentifier')

        # Output
        self.env["version"] = version
        self.output("Version: {}".format(self.env["version"]))
        self.env["bundle_id"] = bundle_id
        self.output("Bundle Identifier: {}".format(self.env["bundle_id"]))

if __name__ == "__main__":
    processor = SolsticeProcessor()
    processor.execute_shell()
