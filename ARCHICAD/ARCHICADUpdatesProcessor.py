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

import json

from autopkglib import ProcessorError, URLGetter


__all__ = ["ARCHICADUpdatesProcessor"]


class ARCHICADUpdatesProcessor(URLGetter):
    """This processor finds the URL for the desired version, localization, and type of ARCHICAD.
    """

    description = __doc__
    input_variables = {
        "major_version": {
            "required": True,
            "description": "The ARCHICAD Major Version to look for available patches.",
        },
        "localization": {
            "required": True,
            "description": "The Localization to looks for available patches.",
        },
        "release_type": {
            "required": True,
            "description": "The release type to look for available patches.",
        }
    }
    output_variables = {
        "url": {"description": "Returns the url to download."},
        "build": {"build":  "Returns the build number."},
        "version": {"description": "Returns the version computed from major_version "
                    "and build number. Same as CFBundleVersion."}
    }


    def main(self):
        """Main process."""

        # Define some variables.
        major_version = self.env.get("major_version")
        localization = self.env.get("localization")
        release_type = self.env.get("release_type")
        available_builds = {}

        # Grab the available downloads.
        response = self.download(
            "https://graphisoft.com/ww/service/downloads/archicad-updates",
            headers={"Accept": "application/json"},
        )
        json_data = json.loads(response)

        # Parse through the available downloads for versions that match the requested parameters.
        for json_object in json_data:
            if all((
                json_object.get("version") == major_version,
                json_object.get("localization") == localization,
                json_object.get("type") == release_type,
                json_object.get("build")
            )):

                mac_link = json_object.get("downloadLinks", dict()).get("mac", dict()).get("url", None)

                if mac_link:
                    available_builds[json_object.get("build")] = f"https://dl.graphisoft.com{mac_link[3:]}"

        # Get the latest version.
        try:
            if available_builds:
                build = sorted(available_builds.keys())[-1]
                version = f"{major_version}.0.0.{build}"
                url = available_builds[build]
                build = str(build)

            self.env["url"] = url
            self.output(f"Download URL: {self.env['url']}", verbose_level=2)
            self.env["build"] = build
            self.output(f"build: {self.env['build']}", verbose_level=2)
            self.env["version"] = version
            self.output(f"version: {self.env['version']}", verbose_level=2)

        except:
            raise ProcessorError("Unable to find a url based on the parameters provided.")


if __name__ == "__main__":
    PROCESSOR = ARCHICADUpdatesProcessor()
    PROCESSOR.execute_shell()
