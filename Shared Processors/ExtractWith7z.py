#!/usr/local/autopkg/python
#
# Copyright 2022 Zack Thompson (MLBZ521)
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

import os
import re
import shutil
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["ExtractWith7z"]


class ExtractWith7z(Processor):
    """This processor extracts files with a specified 7zip binary."""

    description = __doc__
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
    output_variables = {}


    def main(self):

        # Define variables
        archive_path = self.env.get("archive_path", self.env.get("pathname"))

        if not archive_path:
            raise ProcessorError("Path to an archive was not provided!")

        custom_path = self.env.get("7z_path", "")
        destination_path = self.env.get("destination_path", os.path.join(
            self.env["RECIPE_CACHE_DIR"], self.env["NAME"]))

        # Create the directory if needed
        if not os.path.exists(destination_path):

            try:
                os.makedirs(destination_path)
            except OSError as error:
                raise ProcessorError(f"Failed to create {destination_path}:  {error.strerror}") from error

        elif self.env.get("purge_destination"):

            for entry in os.listdir(destination_path):

                path = os.path.join(destination_path, entry)

                try:

                    if os.path.isdir(path) and not os.path.islink(path):
                        shutil.rmtree(path)
                    else:
                        os.unlink(path)

                except OSError as error:
                    raise ProcessorError(f"Failed to remove {path}:  {error.strerror}") from error

        # Check if a custom binary path was provided
        if custom_path and custom_path != "/path/to/7z":

            # Verify the custom binary exists at provided path
            if not os.path.exists(custom_path):
                raise ProcessorError(
                    f"Provided {os.path.basename(custom_path)} binary does not exist at the following path:  {os.path.dirname(custom_path)}")

            self.output(f"Provided {os.path.basename(custom_path)} binary at the following path:  {os.path.dirname(custom_path)}", verbose_level=2)
            binary_7z = [ custom_path ]

        else:
            # Set the binaries we're going to look for
            binary_7z = [ "7zz", "/usr/local/7zz/7zz", "7z", "7za", "7zr", "p7zip", 
                "/usr/local/bin/7z", "/Applications/Keka.app/Contents/MacOS/Keka" ]

        # Success/Fail Flag
        found_binary = False

        # Loop through each binary and check if it exists
        for binary in binary_7z:
            path = shutil.which(binary)

            if path != None:
                found_binary = True

                self.output(f"Using the 7z binary:  {path}", verbose_level=2)

                if re.search("keka", path, re.IGNORECASE):
                    cmd = [
                        f"{path}", 
                        "--client",
                        "7z",
                        "x", 
                        f"{archive_path}", 
                        f"-o{destination_path}"
                    ]
                else:
                    cmd = [
                        f"{path}", 
                        "x", 
                        f"{archive_path}", 
                        f"-o{destination_path}"
                    ]

                try:
                    result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    (_, stderr) = result.communicate()
                except subprocess.CalledProcessError as error:
                    raise ProcessorError(
                        f"{os.path.basename(cmd[0])} execution failed with error code {error.returncode}:  \n{error}") from error

                if result.returncode != 0:
                    raise ProcessorError(
                        f"Extracting {archive_path} with {os.path.basename(cmd[0])} failed with:  {stderr}")

                self.output(f"Extracted {os.path.basename(archive_path)} to {destination_path}")

                break

        if not found_binary:
            raise ProcessorError("ERROR:  Unable to locate a 7z compatible binary!")


if __name__ == "__main__":
    PROCESSOR = ExtractWith7z()
    PROCESSOR.execute_shell()
