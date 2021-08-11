#!/usr/bin/python
#
# Copyright 2019 Zack T (mlbz521)
#
# Inspired by 
#   * Per Olofsson's "Unarchiver.py"
#   * Matt Hansen's "WinInstallerExtractor.py"
#   * Yoann Gini's "Zoom7zUnarchiver.py"
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
import re
import shutil
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["ExtractWith7z"]

class ExtractWith7z(Processor):

    """This processor extracts files with a specified 7zip binary."""

    input_variables = {
        "archive_path": {
            "required": False,
            "description": "Path to an archive. Defaults to contents of the 'pathname'"
                            "variable, for example as is set by URLDownloader."
        },
        "destination_path": {
            "required": False,
            "description": "Directory where archive will be unpacked, created "
                            "if necessary. Defaults to RECIPE_CACHE_DIR/NAME."
        },
        "purge_destination": {
            "required": False,
            "description": "Whether the contents of the destination directory "
                           "will be removed before unpacking."
        },
        "7z_path": {
            "required": False,
            "description": "Path to a 7z-compatible binary.  This does not ship"
                            "with macOS, it will need to be installed manually."
                            "The processor will prioritize a provided binary, but"
                            "if it cannot locate it, it'll continue trying to find"
                            "a 7z-compatible binary in common locations, including"
                            "the system PATH."
        }
    }
    output_variables = {
    }

    description = __doc__

    def main(self):

        # Define variables
        archive_path = self.env.get("archive_path", self.env.get("pathname"))

        if not archive_path:
            raise ProcessorError(
                "Path to an archive was not provided!")

        custom_path = self.env.get("7z_path", "")
        destination_path = self.env.get("destination_path", os.path.join(
            self.env["RECIPE_CACHE_DIR"], self.env["NAME"]))

        # Create the directory if needed
        if not os.path.exists(destination_path):

            try:
                os.makedirs(destination_path)
            except OSError as err:
                raise ProcessorError("Failed to create {}:  {}".format(
                    destination_path, err.strerror))

        elif self.env.get("purge_destination"):

            for entry in os.listdir(destination_path):

                path = os.path.join(destination_path, entry)

                try:

                    if os.path.isdir(path) and not os.path.islink(path):
                        shutil.rmtree(path)
                    else:
                        os.unlink(path)

                except OSError as err:
                    raise ProcessorError("Failed to remove {}:  {}".format(
                        path, err.strerror))

        # Check if a custom binary path was provided
        if custom_path and custom_path != "/path/to/7z":

            # Verify the custom binary exists at provided path
            if not os.path.exists(custom_path):
                raise ProcessorError(
                    "Provided {} binary does not exist at the following path:  {}".format(
                        os.path.basename(custom_path), os.path.dirname(custom_path)))

            self.output("Provided {} binary at the following path:  {}".format(
                os.path.basename(custom_path), os.path.dirname(custom_path)), verbose_level=2)
            binary_7z = [ custom_path ]

        else:
            # Set the binaries we're going to look for
            binary_7z = ["7z", "7za", "7zr", "p7zip", "/usr/local/bin/7z", 
                "/Applications/Keka.app/Contents/MacOS/Keka"]

        # Success/Fail Flag
        found_binary = False

        # Loop through each binary and check if it exists
        for binary in binary_7z:
            path = shutil.which(binary)

            if path != None:
                found_binary = True

                self.output("Using the 7z binary:  {}".format(path), verbose_level=2)

                if re.search("keka", path, re.IGNORECASE):
                    cmd = [
                        "{}".format(path), 
                        "--client",
                        "7z",
                        "x", 
                        "{}".format(archive_path), 
                        "-o{}".format(destination_path)
                    ]
                else:
                    cmd = [
                        "{}".format(path), 
                        "x", 
                        "{}".format(archive_path), 
                        "-o{}".format(destination_path)
                    ]

                try:
                    result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    (_, stderr) = result.communicate()
                except subprocess.CalledProcessError as error:
                    raise ProcessorError(
                        "{} execution failed with error code {}:  \n{}".format(
                            os.path.basename(cmd[0]), error.returncode, error))

                if result.returncode != 0:
                    raise ProcessorError(
                        "Extracting {} with {} failed with:  {}".format(
                            archive_path, os.path.basename(cmd[0]), stderr))

                self.output("Extracted {} to {}".format(
                    os.path.basename(archive_path), destination_path))

                break

        if not found_binary:
            raise ProcessorError("ERROR:  Unable to locate a 7z compatible binary!")


if __name__ == "__main__":
    processor = ExtractWith7z()
    processor.execute_shell()
