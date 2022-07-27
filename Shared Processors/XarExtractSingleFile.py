#!/usr/local/autopkg/python
#
# Copyright 2022 by Zack T (MLBZ521)
#
# Inspired by DistributionPkgInfo.py from dataJar
#   https://github.com/autopkg/dataJAR-recipes/blob/master/Shared%20Processors/DistributionPkgInfo.py
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

"""See docstring for XarExtractSingleFile class"""

import os.path
import shlex
import subprocess

from fnmatch import fnmatch

from autopkglib import ProcessorError
from autopkglib.DmgMounter import DmgMounter


__all__ = ["XarExtractSingleFile"]


class XarExtractSingleFile(DmgMounter):
    """Extracts a single file from an archive using xar.  Archive path 
    can be within a .dmg which will be mounted."""

    description = __doc__

    input_variables = {
        "archive_path": {
            "required": True,
            "description": ("Path to archive. Can point to an archive "
            "inside a .dmg which will be mounted.")
        },
        "extract_file_path": {
            "required": False,
            "description": "Path to extract the file to."
            "Default:  extractedfile"
        },
        "file_to_extract": {
            "required": True,
            "description": "File to extract out of the archive."
        }
    }

    output_variables = {
        "extracted_file": {
            "description": "The file that was extracted from the archive."
        }
    }

    def runUtility(self, command):
        """A helper function for subprocess.
        Args:
            command:  Must be a string.
        Returns:
            Results in a dictionary.
        """

        # Validate that command is a string
        if not isinstance(command, str):
            raise TypeError('Command must be in a str')

        command = shlex.split(command)

        process = subprocess.Popen( 
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False )
        (stdout, stderr) = process.communicate()

        return {
            "stdout": (stdout).strip(),
            "stderr": (stderr).strip() if stderr != None else None,
            "status": process.returncode,
            "success": True if process.returncode == 0 else False
        }


    def main(self):

        # Define variables
        source_path = os.path.normpath(self.env["archive_path"])
        extract_file_path = self.env.get("extract_file_path", 
            os.path.join(self.env.get("RECIPE_CACHE_DIR"), "extractedfile")
        )
        file_to_extract = self.env["file_to_extract"]
        found_match = False

        # Check to see if the source_path is a dmg
        (dmg_path, dmg, dmg_source_path) = self.parsePathForDMG(source_path)

        if dmg:

            self.output(
                f"Parsed dmg results: dmg_path: {dmg_path}, dmg: {dmg}, dmg_source_path: {dmg_source_path}", 
                verbose_level=2
            )

            try:
                mount_point = self.mount(dmg_path)
                source_path = os.path.join(mount_point, dmg_source_path)

            except Exception as error:
                raise ProcessorError("Unable to mount the dmg.") from error

        # Wrap in a try/finally so if a dmg is mounted, it will always be unmounted
        try:

            # Get a list of files in the archive
            cmd_list_files = f'/usr/bin/xar -tf "{source_path}"'
            results_list_files = self.runUtility(cmd_list_files)

            if not results_list_files['success']:
                raise ProcessorError(
                    f"Failed to list the files in the archive:  {source_path} -- due to error:  {results_list_files['stderr']}")

            # Split the file names
            list_of_files = (results_list_files['stdout'].decode("utf-8")).split('\n')

            # Create destination directory if it doesn't exist
            if not os.path.exists(extract_file_path):
                try:
                    os.mkdir(extract_file_path)
                except OSError as error:
                    raise ProcessorError(f"Can't create {extract_file_path}:  {error.strerror}") from error

            # Find a match in the list of files
            match = [ item for item in list_of_files if fnmatch(item, file_to_extract) ]

            # Ensure there was only one match
            if len(match) != 1:
                raise ProcessorError(
                    "Multiple matches found in the archive.  Only one file is supported to be extracted.")

            match = match[0]

            cmd_extract = f'/usr/bin/xar -xf "{source_path}" "{match}" -C "{extract_file_path}"'
            results_list_files = self.runUtility(cmd_extract)

            if not results_list_files['success']:
                raise ProcessorError(
                    f"Failed to extract the archive:  {source_path} -- due to error:  {results_list_files['stderr']}")

            # Path to the extract file
            extracted_file = os.path.join(extract_file_path, match)

            # Verify file exists
            if not os.path.exists(extracted_file):
                raise ProcessorError(f"Cannot find the file:  {file_to_extract}")

            self.output(f'extracted_file:  {extracted_file}')
            self.env["extracted_file"] = extracted_file

        finally:
            if dmg:
                self.unmount(dmg_path)


if __name__ == '__main__':
    PROCESSOR = XarExtractSingleFile()
    PROCESSOR.execute_shell()
