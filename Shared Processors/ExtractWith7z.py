#!/usr/bin/python
#
# Copyright 2019 Zack T (mlbz521)
#
# Inspired by Per Olofsson's "Unarchiver.py", Matt Hansen's "WinInstallerExtractor.py", and Yoann Gini's "Zoom7zUnarchiver.py"
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
import shutil
import subprocess

from autopkglib import Processor, ProcessorError

try:
    from shutil import which as find_binary # For Python 3
except ImportError:
    from distutils.spawn import find_executable as find_binary # For Python 2

__all__ = ["ExtractWith7z"]

class ExtractWith7z(Processor):

    """This processor extracts files with a specified 7zip binary."""

    input_variables = {
        "archive_path": {
            "required": False,
            "description": "Path to an archive. Defaults to contents of the "
                           "'pathname' variable, for example as is set by "
                           "URLDownloader."
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
        custom_path = self.env.get('7z_path', '')
        archive_path = self.env.get("archive_path", self.env.get("pathname"))
        if not archive_path:
            raise ProcessorError(
                "Expected an 'archive_path' input variable but none is set!")
        destination_path = self.env.get("destination_path", os.path.join(self.env["RECIPE_CACHE_DIR"], self.env["NAME"]))

        # Create the directory if needed
        if not os.path.exists(destination_path):
            try:
                os.makedirs(destination_path)
            except OSError as err:
                raise ProcessorError("Failed to create {destination_path}:  {error}".format(destination_path=destination_path, error=err.strerror))
        elif self.env.get('purge_destination'):
            for entry in os.listdir(destination_path):
                path = os.path.join(destination_path, entry)
                try:
                    if os.path.isdir(path) and not os.path.islink(path):
                        shutil.rmtree(path)
                    else:
                        os.unlink(path)
                except OSError as err:
                    raise ProcessorError("Failed to remove {path}:  {error}".format(path=path, error=err.strerror))

        # Set the binaries we're going to look for
        binary_7z = ['7z', '7za', '7zr', 'p7zip', 'keka7z', '/usr/local/bin/7z', '/Applications/Keka.app/Contents/Resources/keka7z']

        # If a custom binary path was provided, add it at the front of our list
        if custom_path and custom_path != '%BINARY_7Z_PATH%':
            self.output("Provided {filename} binary at the following path:  {custom_path}".format(filename=os.path.basename(custom_path), custom_path=os.path.dirname(custom_path)))
            binary_7z.insert(0, custom_path)

        # Success/Fail Flag
        found_binary = '1'

        # Loop through each binary and check if it exists
        for binary in binary_7z:
            if find_binary(binary):
                # Binary must exist, so build the command to run it
                self.output("Using the {filename} binary at the following path:  {path}".format(filename=os.path.basename(binary), path=os.path.dirname(binary)))
                cmd = ['{binary}'.format(binary=binary), 'x', '{archive_path}'.format(archive_path=archive_path), '-o{destination_path}'.format(destination_path=destination_path)]

                try:
                    result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    (_, stderr) = result.communicate()
                except subprocess.CalledProcessError as error:
                    raise ProcessorError('{binary} execution failed with error code {error_code}:  \n{error}'.format(binary=os.path.basename(cmd[0]), error_code=error.returncode, error=error))
                
                if result.returncode != 0:
                    raise ProcessorError("Extracting {archive_path} with {binary} failed with:  {error}".format(archive_path=archive_path, binary=os.path.basename(cmd[0]), error=stderr))

                self.output("Extracted {filename} to {destination_path}".format(filename=os.path.basename(archive_path), destination_path=destination_path))

                found_binary = '0'
                break
            
        if found_binary != '0':
            raise ProcessorError("ERROR:  Unable to locate a 7z compatible binary!")

if __name__ == '__main__':
    processor = ExtractWith7z()
    processor.execute_shell()
