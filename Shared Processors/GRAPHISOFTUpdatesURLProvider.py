#!/usr/local/autopkg/python
#
# Copyright 2026 Zack Thompson (MLBZ521)
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

from html.parser import HTMLParser
from operator import itemgetter

from autopkglib import ProcessorError, URLGetter


__all__ = ["GRAPHISOFTUpdatesURLProvider"]


class GRAPHISOFTUpdatesURLProvider(URLGetter):
	"""This processor finds the URL for the latest build of the desired major 
		version and other parameters for Graphisoft applications.
		
		NOTE:  So far, this has only been tested with the "product" 'Archicad', 
		but the framework should work with other "product" types.
	"""

	description = __doc__
	input_variables = {
		"product": {
			"required": True,
			"description": "The Graphisoft application to look for available updates."
		},
		"major_version": {
			"required": True,
			"description": "The application major version to filter for."
		},
		"localization": {
			"required": True,
			"description": "The Localization to filter for."
		},
		"edition": {
			"required": True,
			"description": "The Edition to filter for."
		},
		"platform": {
			"required": True,
			"description": "The OS Platform to filter for.  "
			"macOS_Universal is also supported. as a custom option."
		}
	}
	output_variables = {
		"url": {"description": "Returns the url to download."},
		"arm_url": {"description": "Returns the url to download for an ARM specific build."},
		"intel_url": {"description": "Returns the url to download for an Intel specific build."},
		"build": {"description":  "Returns the build number."},
		"arm_build": {"description":  "Returns the build number for an ARM specific build."},
		"intel_build": {"description":  "Returns the build number for an Intel specific build."},
		"version": {"description": "Returns the version computed from major_version "
					"and build number. Same as CFBundleVersion."},
		"arm_version": {"description": "Returns the version computed from major_version "
					"and build number. Same as CFBundleVersion. For an ARM specific build."},
		"intel_version": {"description": "Returns the version computed from major_version "
					"and build number. Same as CFBundleVersion. For an Intel specific build."},
		"arch": {"description": "Returns the architecture for the downloaded installer,"
					"if not universal."}
	}


	def main(self):
		"""Main process."""

		# Define some variables.
		# product is "type", options are:
			# [None, 'Archicad', 'BIMx', 'DDScad Viewer', 'BIMcloud', 'DDScad', 'Archicad Library', 'MEP Designer']
		product = self.env.get("product")
		# major_version is "versions", example options are:
			# ['24', '2021', '25', '2022', '26', None, '2023', '27', '2024', '28', '2021.1', '2021.2', '2022.1', '2022.3', '2023.1', '2023.3', '2024.1', '2024.3', '18', '19', '20', '28.0', '28.1', '2025.1', '28.2', '29', '2025.3', '21', '29.0.1', '2026.1']
		major_version = self.env.get("major_version")
		# localization is "locale", example options are:
			# ['AUS', 'AUT', 'BRA', 'CHE', 'CHI', 'CZE', 'FIN', 'FRA', 'GER', 'GRE', 'HUN', 'INT', 'ITA', 'JPN', 'KOR', 'NED', 'NOR', 'NZE', 'POL', 'POR', 'RUS', 'SPA', 'SWE', 'TAI', 'TUR', 'UKI', 'UKR', 'USA', None, 'NLD']
		locale = self.env.get("localization")
		# edition example options are:
			# ['FULL', 'SOLO', 'START', None, 'BTC', 'BIMcloud', 'DDScad', 'MEP Designer']
		edition = self.env.get("edition")
		# platform options are: [1, 2, 3, 4, 5, 7, 6]
			# 1 = macOS ARM
			# 2 = macOS Intel
			# 3 = Windows
			# 4 = ?
			# 5 = ?
			# 6 = macOS Intel (for BIMcloud)
			# 7 = ?
		platform = self.env.get("platform")
		match platform:
			case "macOS_Universal":
				platform = "Universal"
			case "macOS_ARM":
				platform = 1
				self.env["arch"] = "ARM"
			case "macOS_Intel":
				platform = 2
				self.env["arch"] = "Intel"
			case "Windows":
				platform = 3
		# Not currently filtering for categories, not sure what they identify yet
		# category options are: [1, 2, 6]


		class MyHTMLParser(HTMLParser):


			def __init__(self):
				HTMLParser.__init__(self)
				self.data = ""


			def handle_starttag(self, tag, attributes):
				if tag == "downloads":
					self.tracking = True
					self.data = attributes
					return


		# Grab the available downloads.
		response = self.download(
			"https://www.graphisoft.com/en-us/downloads/?section=update",
			headers={"Accept": "application/json"},
		)

		parser = MyHTMLParser()
		parser.feed(response.decode())
		updates = json.loads(parser.data[1][1])

		try:

			if platform == "Universal":

				arm_platform_updates = list(
					filter(
						lambda d:
							d['platform'] == 1 and
							d['type'] == product and
							d['version'] == major_version and
							d['locale'] == locale and
							d['edition'] == edition,
					updates)
				)
				intel_platform_updates = list(
					filter(
						lambda d:
							d['platform'] == 2 and
							d['type'] == product and
							d['version'] == major_version and
							d['locale'] == locale and
							d['edition'] == edition,
					updates)
				)

				# Reverse sort based on build number and get the first one
				arm_update = sorted(arm_platform_updates, key=itemgetter('build'), reverse=True)[0]
				intel_update = sorted(intel_platform_updates, key=itemgetter('build'), reverse=True)[0]

				if not ( arm_update and intel_update ):
					ProcessorError("Unable to find urls based on the parameters provided.")

				self.env["arm_url"] = arm_update.get("data", dict()).get("url", None)
				self.env["intel_url"] = intel_update.get("data", dict()).get("url", None)
				self.env["arm_build"] = str(arm_update.get("build"))
				self.env["intel_build"] = str(intel_update.get("build"))
				self.env["arm_version"] = f"{major_version}.0.0.{self.env['arm_build']}"
				self.env["intel_version"] = f"{major_version}.0.0.{self.env['intel_build']}"

			else:
				# Parse through the available downloads for versions that match the requested parameters.
				matching_updates = list(
					filter(
						lambda d:
							d['platform'] == platform and
							d['type'] == product and
							d['version'] == major_version and
							d['locale'] == locale and
							d['edition'] == edition,
					updates)
				)

				# Reverse sort based on build number and get the first one
				matching_update = sorted(matching_updates, key=itemgetter('build'), reverse=True)[0]

				if not matching_update:
					ProcessorError("Unable to find a url based on the parameters provided.")

				url = matching_update.get("data", dict()).get("url", None)
				self.env["url"] = url
				self.env["build"] = str(matching_update.get("build"))
				self.env["version"] = f"{major_version}.0.0.{self.env['build']}"

		except:
			raise ProcessorError("Unable to find a url based on the parameters provided.")


if __name__ == "__main__":
	PROCESSOR = GRAPHISOFTUpdatesURLProvider()
	PROCESSOR.execute_shell()
