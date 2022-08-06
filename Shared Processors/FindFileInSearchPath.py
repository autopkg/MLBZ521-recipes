#!/usr/local/autopkg/python
#
# Copyright 2022 Zack Thompson (MLBZ521)
#   Borrowed and customized the find_file_in_search_path function from JSSImporter.py
#       https://github.com/jssimporter/JSSImporter/blob/master/JSSImporter.py
#
# Copyright 2014-2017 Shea G. Craig
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

from collections import OrderedDict
from autopkglib import Processor, ProcessorError


__all__ = ["FindFileInSearchPath"]


class FindFileInSearchPath(Processor):
    """Search search_paths for the first existing instance of path.
    Searches, in order, through the following directories
    until a matching file is found:
        1. Path as specified.
        2. The parent folder of the path.
        3. First ParentRecipe's folder.
        4. First ParentRecipe's parent folder.
        5. Second ParentRecipe's folder.
        6. Second ParentRecipe's parent folder.
        7. Nth ParentRecipe's folder.
        8. Nth ParentRecipe's parent folder.
    This search-path method is primarily in place to
    support using recipe overrides. It allows users to avoid having
    to copy templates, icons, etc, to the override directory.

    *** Additional functionality added to support storing files in a sub 
    directory of the recipes parent directory. ***

    Args:
        path: String filename or path to file.
            If path is just a filename, path is assumed to
            be self.env["RECIPE_DIR"].
    Returns:
        Absolute path to the first match in search paths.
    Raises:
        ProcessorError if none of the above files exist.
    """

    description = __doc__
    input_variables = {
        "find_file": {
            "required": True,
            "description": "The name of the file to find in the search_paths."
        }
    }
    output_variables = {
        "path_to_found_file": {
            "description": "Full path to the file."
        }
    }


    def main(self):

        find_file = self.env.get('find_file')
        sub_directory = False

        # Ensure input is expanded.
        path = os.path.expanduser(find_file)

        # Check to see if path is a filename.
        if not os.path.dirname(path):
            # If so, assume that the file is meant to be in the recipe directory.
            path = os.path.join(self.env["RECIPE_DIR"], path)
        else:
            # In case files are stored in a sub directory of the recipes parent directory.
            sub_directory = True

        filename = os.path.basename(path)
        parent_recipe_dirs = [os.path.dirname(parent) for parent in self.env["PARENT_RECIPES"]]
        unique_parent_dirs = OrderedDict()

        for parent in parent_recipe_dirs:
            unique_parent_dirs[parent] = parent

        search_dirs = ([os.path.dirname(path)] + list(unique_parent_dirs))
        tested = []
        final_path = ""

        # Look for the first file that exists in the search_dirs and their parent folders.
        for search_dir in search_dirs:
            test_path = os.path.join(search_dir, filename)
            test_parent_folder_path = os.path.abspath(os.path.join(search_dir, "..", filename))

            if os.path.exists(test_path):
                final_path = test_path

            elif os.path.exists(test_parent_folder_path):
                final_path = test_parent_folder_path

            elif sub_directory:
                test_sub_directory = search_dir + path

                if os.path.exists(test_sub_directory):
                    final_path = test_sub_directory
                tested.append(test_sub_directory)

            tested.extend((test_path, test_parent_folder_path))

            if final_path:
                break

        if not final_path:
            raise ProcessorError(f"Unable to find file {filename} at any of the following locations: {tested}")

        # Return values
        self.env["path_to_found_file"] = final_path
        self.output(f"Path to found file: {self.env['path_to_found_file']}")


if __name__ == "__main__":
    PROCESSOR = FindFileInSearchPath()
    PROCESSOR.execute_shell()
