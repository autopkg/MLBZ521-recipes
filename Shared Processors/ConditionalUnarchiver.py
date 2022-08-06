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
import re

from autopkglib import Processor, ProcessorError, FileFinder, Unarchiver, is_mac


__all__ = ["ConditionalUnarchiver"]


def _default_use_python_native_extractor() -> bool:
    return not is_mac()


class ConditionalUnarchiver(Processor):
    """This process provides a condition wrapper around the Core Unarchiver Processor.

    If extraction is needed, it uses Unarchiver to do and then (optionally) uses the FileFinder 
    Processor to locate an extracted file.

    If extraction is not needed, the processor simply assigns the %pathname% env variable to the 
    %found_filename% env variable.
    """

    description = __doc__

    input_variables = {
        "archive_path": {
            "required": False,
            "description": "Path to an archive. Defaults to contents of the "
            "'pathname' variable, for example as is set by "
            "URLDownloader.",
        },
        "destination_path": {
            "required": False,
            "description": (
                "Directory where archive will be unpacked, created "
                "if necessary. Defaults to RECIPE_CACHE_DIR/NAME."
            ),
        },
        "purge_destination": {
            "required": False,
            "description": "Whether the contents of the destination directory "
            "will be removed before unpacking.",
        },
        "archive_format": {
            "required": False,
            "description": (
                "The archive format. Currently supported: 'zip', "
                "'tar_gzip', 'tar_bzip2', 'tar'. If omitted, the "
                "file extension is used to guess the format."
            ),
        },
        "USE_PYTHON_NATIVE_EXTRACTOR": {
            "required": False,
            "description": (
                "Controls whether or not Unarchiver extracts the archive with native "
                "Python code, or calls out to a platform specific utility. "
                "The default is determined on a platform specific basis. "
                "Currently, this means that on macOS platform utilities are used, "
                "and otherwise Python is used."
            ),
            "default": _default_use_python_native_extractor(),
        },
        "find_extracted_file_pattern": {
            "required": False,
            "description": "Shell glob pattern to match files by."
        }
    }

    output_variables = {
        "found_filename": {
            "description": "Returns the url to download."
        }
    }


    def main(self):
        """Do the main thing."""

        destination_path = self.env.get(
            "destination_path",
            os.path.join(self.env["RECIPE_CACHE_DIR"], self.env["NAME"]),
        )

        if not re.search(r".+\.(zip|tar_gzip|tar_bzip2|tar)$", self.env.get("pathname")):

            self.output("File is NOT an archive...", verbose_level=2)
            self.env["found_filename"] = self.env.get("pathname")

            # This is a hack to prevent an error in a .pkg recipe that may have a PathDeleter
            # step to delete the directory where the contents are extracted too.
            if not os.path.exists(destination_path):
                try:
                    os.makedirs(destination_path)
                except OSError as err:
                    raise ProcessorError(f"Can't create {destination_path}: {err.strerror}") from err

        else:

            self.output("File is an archive...", verbose_level=2)

            # Decompress the archive
            unarchive = Unarchiver()
            unarchive.env = self.env
            unarchive.process()
            unarchive.main()

            find_extracted_file_pattern = self.env.get("find_extracted_file_pattern", None)

            if find_extracted_file_pattern:

                # Find the requested file type within the destination path
                file_finder = FileFinder()
                self.env["pattern"] = f"{destination_path}/{find_extracted_file_pattern}"
                file_finder.env = self.env
                file_finder.process()
                file_finder.main()


if __name__ == "__main__":
    PROCESSOR = ConditionalUnarchiver()
    PROCESSOR.execute_shell()
