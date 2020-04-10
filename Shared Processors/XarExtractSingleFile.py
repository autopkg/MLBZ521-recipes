#!/usr/bin/python
#
# XarExtractSingleFile.py Copyright 2020 by Zack Thompson (MLBZ521)
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

from __future__ import absolute_import

import os.path
import shlex
import subprocess

from fnmatch import fnmatch
from autopkglib import Processor, ProcessorError

__all__ = ["XarExtractSingleFile"]


class XarExtractSingleFile(Processor):
    """Extracts a single file from an archive using xar."""

    description = __doc__

    input_variables = {
        "archive_path": {
            "required": True,
            "description": ("Path to archive to extract.")
        },
        "extract_file_path": {
            "required": False,
            "description": ("Path to extract the file to."
            "Deafault:  extractedfile")
        },
        "file_to_extract": {
            "required": True,
            "description": ("File to extract out of the archive.")
        }
    }

    output_variables = {
        "extracted_file": {
            "description": ("The file that was extracted from the archive.")
        }
    }

    description = __doc__

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

        process = subprocess.Popen( command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False )
        (stdout, stderr) = process.communicate()

        result_dict = {
            "stdout": (stdout).strip(),
            "stderr": (stderr).strip() if stderr != None else None,
            "status": process.returncode,
            "success": True if process.returncode == 0 else False
        }

        return result_dict

    def main(self):

        # Define variables
        archive_path = os.path.join(self.env["archive_path"])
        extract_file_path = self.env.get("extract_file_path", os.path.join(self.env.get("RECIPE_CACHE_DIR"), "extractedfile"))
        file_to_extract = self.env["file_to_extract"]
        found_match = False

        # Get a list of files in the archive
        cmd_list_files = '/usr/bin/xar -tf "{}"'.format(archive_path)
        # cmd_list_files = '/Users/zthomps3/Downloads/xar -tf "{}"'.format(archive_path)
        results_list_files = self.runUtility(cmd_list_files)

        if not results_list_files['success']:
            raise ProcessorError("Failed to list the files in the archive:  {archive_path} -- due to error:  {error}".format(archive_path=archive_path, error=results_list_files['stderr']))

        # Split the file names
        list_of_files = (results_list_files['stdout'].decode("utf-8")).split('\n')

        # Create destintation directory if it doesn't exist
        if not os.path.exists(extract_file_path):
            try:
                os.mkdir(extract_file_path)
            except OSError as err:
                raise ProcessorError("Can't create {}:  {}".format(extract_file_path, err.strerror))

        # Walk trough the list of files entries
        for filename in [ item for item in list_of_files if fnmatch(item, file_to_extract) ]:
            cmd_extract = '/usr/bin/xar -xf "{archive_path}" "{filename}" -C "{extract_file_path}"'.format(archive_path=archive_path, filename=filename, extract_file_path=extract_file_path)
            # cmd_extract = '/Users/zthomps3/Downloads/xar -xf "{archive_path}" "{filename}" -C "{extract_file_path}"'.format(archive_path=archive_path, filename=filename, extract_file_path=extract_file_path)
            results_list_files = self.runUtility(cmd_extract)

            if not results_list_files['success']:
                raise ProcessorError("Failed to extract the archive:  {archive_path} -- due to error:  {error}".format(archive_path=archive_path, error=results_list_files['stderr']))

            # Path to the extract file
            extracted_file = os.path.join(extract_file_path, filename)

        # Verify file exists
        for filename in os.listdir(extract_file_path):
            if fnmatch(filename, file_to_extract):
                found_match = True

        if found_match == True:
            self.output('extracted_file:  {}'.format(extracted_file))
            self.env["extracted_file"] = extracted_file
        else:
            raise ProcessorError("Cannot find the file:  {}".format(file_to_extract))


if __name__ == '__main__':
    PROCESSOR = XarExtractSingleFile()
    processor.execute_shell()
