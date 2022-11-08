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

from autopkglib import Processor, ProcessorError


__all__ = ["RenamePath"]


class RenamePath(Processor):
	"""This processor will rename a file directory.

	If the name file name ends with '.pkg', the %pkg_path% variable will 
	be updated with the new full path.
	"""

	description = __doc__
	input_variables = {
		"source_path": {
			"required": True,
			"description": "Full path to a file or directory that "
				"needs to be renamed."
		},
		"new_name": {
			"required": True,
			"description": "The new name of the file or directory."
				"If 'new_name' ends with '.pkg', the pkg_path variable will "
				"be updated with the new path."
		},
		"return_variable": {
			"required": False,
			"description": "The desired variable name to assign the value to."
				"See 'new_name' description for additional logic information."
		},
		"update_pkg_path": {
			"required": False,
			"description": "Automatically update pkg_path. Defaults to True.",
			"default": True
		}
	}
	output_variables = {
		"return_variable": {
			"description": "The variable that the new path was set too."
		}
	}


	def main(self):

		source_path = self.env["source_path"]
		new_name = self.env.get("new_name")
		update_pkg_path = self.env["update_pkg_path"]
		return_variable = self.env.get("return_variable", None)

		# Ensure the path exists
		if not os.path.exists(source_path):
			raise ProcessorError("Path does not exist")

		# Rename the path
		root, _ = os.path.split(source_path)
		new_path = os.path.join(root, new_name)
		os.rename(source_path, new_path)

		# if Path ends with ".pkg" update the %pkg_path% with the new value
		if update_pkg_path and re.search(r"[.]pkg$", new_name, re.IGNORECASE):

			self.output(f"Updating %pkg_path% to:  {new_path}", verbose_level=2)
			self.env["pkg_path"] = new_path
			self.env["return_variable"] = "pkg_path"

		elif return_variable:

			self.env["return_variable"] = return_variable
			self.env[return_variable] = new_path


if __name__ == "__main__":
	PROCESSOR = RenamePath()
	PROCESSOR.execute_shell()
