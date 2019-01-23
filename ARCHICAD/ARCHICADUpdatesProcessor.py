#!/usr/bin/env python
#
# Copyright 2019 Zack T (mlbz521)
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
import requests
import subprocess
import sys
from autopkglib import Processor, ProcessorError

__all__ = ["ARCHICADUpdatesProcessor"]

class ARCHICADUpdatesProcessor(Processor):

    """This processor finds the URL for the desired version, localization, and type of ARCHICAD.
    """

    input_variables = {
        "major_version": {
            "required": True,
            "description": "The ARCHICAD Major Version to look for available patches.",
        },
        "localization": {
            "required": True,
            "description": "The Localization to looks for available patches.",
        },
        "relase_type": {
            "required": True,
            "description": "The release type to look for avialable patches.",
        }
    }
    output_variables = {
        "url": {
            "description": "Returns the url to download."
        },
        "version": {
            "description": "Returns the build number as the version."
        }
    }

    description = __doc__

    def main(self):

        # Define some variables.
        major_version = self.env.get("major_version")
        localization = self.env.get("localization")
        relase_type = self.env.get("relase_type")
        available_builds = {}

        try:
            # Grab the available downloads.
            response = requests.get('https://www.graphisoft.com/downloads/db-v3.json')
            json_data = response.json()
        except Exception:
            # If requests fails (running on macOS 10.12 or older), resort to using curl.
            sys.exc_clear()

            # Build the command.
            curl_cmd = ['/usr/bin/curl', '--silent', '--show-error', '--no-buffer', '--fail',
                        '--speed-time', '30',
                        '--location',
                        '--header', 'Accept: application/json'
                        '--url', 'https://www.graphisoft.com/downloads/db-v3.json']
            try:
                response = subprocess.check_output(curl_cmd)
                json_data = json.loads(response)
            except subprocess.CalledProcessError as error:
                print ('return code = ', error.returncode)
                print ('result = ', error)  

        # Parse through the available downloads for versions that match the requested paramters.
        for json_Object in json_data:
            if json_Object.get('version') == major_version:
                if json_Object.get('localization') == localization:
                    if json_Object.get('type') == relase_type:
                        for details in json_Object['downloadLinks']:
                            if details.get('platform') == 'mac':
                                available_builds[json_Object.get('build')] = details['url']

        # Get the latest version.
        build = sorted(available_builds.keys())[-1]
        url = available_builds[build]

        if url:
            self.env["url"] = url
            self.output("Download URL: {}".format(self.env["url"]))
            self.env["version"] = build
            self.output("version: {}".format(self.env["version"]))
        else:
            raise ProcessorError("Unable to find a url based on the parameters provided.")

if __name__ == "__main__":
    processor = ARCHICADUpdatesProcessor()
    processor.execute_shell()
