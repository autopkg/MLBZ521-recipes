#!/usr/local/autopkg/python
#
# Copyright 2024 Zack Thompson (MLBZ521)
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

import json

from autopkglib import ProcessorError, URLGetter


__all__ = ["MapleURLProvider"]


class MapleURLProvider(URLGetter):
	"""This processor obtains the download URL for Maple for the supplied Purchase Code."""

	description = __doc__
	input_variables = {
		"purchase_code": {
			"required": True,
			"description": (
				"The Purchase Code is emailed to you from Maplesoft and is unique for each major ",
				"version.  It can be one of three types:  Network, Standalone, or Homeuse."
			)
		}
	}
	output_variables = {
		"url": {
			"description": "Returns the url to download."
		},
		"installed_version": {
			"description": "Returns the reported version string."
		}
	}


	def main(self):

		# Define variables
		purchase_code = self.env.get("purchase_code")

		if not purchase_code:
			raise ProcessorError("Expected the 'purchase_code' input variable but none is set!")

		# Build the URL
		lookup_url = f"https://www.maplesoft.com/download/purchaseCodeInfo.aspx?PC={purchase_code}"

		# Look up the purchase code
		response = self.download(lookup_url)

		if response:
			response_object = json.loads(response.decode())
			self.output(f"Results:  \n{response_object}", verbose_level=3)
			if response_object.get("status") == "OK":
				for product in response_object.get("products"):
					url = product.get("download")
					version = product.get("product").split("Maple ")[1]
			else:
				raise ProcessorError(f"Error looking up purchase code:  \n{response_object}")

			# Return results
			self.env["url"] = url
			self.output(f"Download URL: {self.env['url']}", verbose_level=2)
			self.env["installed_version"] = version
			self.output(f"installed_version: {self.env['installed_version']}", verbose_level=2)

		else:
			raise ProcessorError("Error:  No response back from lookup url.")


if __name__ == "__main__":
	PROCESSOR = MapleURLProvider()
	PROCESSOR.execute_shell()
