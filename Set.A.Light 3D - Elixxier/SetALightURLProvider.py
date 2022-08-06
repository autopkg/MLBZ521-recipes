#!/usr/local/autopkg/python
#
# Copyright 2021 Zack Thompson (MLBZ521)
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
"""See docstring for SetALightURLProvider class"""

import re

from autopkglib import ProcessorError, URLDownloader


__all__ = ["SetALightURLProvider"]


class SetALightURLProvider(URLDownloader):
    """This processor finds the URL for the Set.A.Light 3D download."""

    description = __doc__
    input_variables = {
        "SEARCH_URL": {
            "description": "URL to search.",
            "required": True,
        }
    }
    output_variables = {
        "url": {
            "description": ("URL to download.")
        }
    }


    def main(self):

        # Get environment variables
        search_url = self.env.get("SEARCH_URL")

        try:
            # Initialize the curl_cmd with the required curl switches
            curl_opts = [
                self.curl_binary(),
                "--url", f"{search_url}",
                "--request", "GET",
                "--silent",
                "--show-error",
                "--no-buffer",
                "--dump-header", "-",
                "--fail"
            ]

            # Execute curl
            stdout, stderr, returncode = self.execute_curl(curl_opts)
            parse_results = stdout.split('\n')

            for item in parse_results:
                if re.search("location: ", item):
                    self.env["url"] = (item.split(": ")[-1]).replace(" ", "%20")
                    self.output(f"Download URL: {self.env['url']}")

        except:
            raise ProcessorError("Failed to identify the URL to download.")


if __name__ == "__main__":
    PROCESSOR = SetALightURLProvider()
    PROCESSOR.execute_shell()
