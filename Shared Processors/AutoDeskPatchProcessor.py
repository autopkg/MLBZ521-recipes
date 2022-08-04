#!/usr/local/autopkg/python
#
# Copyright 2020 Zack Thompson (mlbz521)
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

__all__ = ["AutoDeskPatchProcessor"]

class AutoDeskPatchProcessor(URLGetter):

    """This processor finds the URL for the latest patch of the supplied major
    version of AutoDesk."""

    input_variables = {
        "product": {
            "required": True,
            "description": "Which AutoDesk Major Version to look for available patches.",
        },
        "major_version": {
            "required": True,
            "description": "Which AutoDesk Major Version to look for available patches.",
        }
    }
    output_variables = {
        "search_url": {
            "description": "Returns the url to download."
        },
        "search_pattern": {
            "description": "Returns the pattern to search for in the search_url."
        }
    }

    description = __doc__

    def main(self):

        # Define variables
        product = self.env.get('product')
        major_version = self.env.get('major_version')

        if not product:
            raise ProcessorError(
                "Expected an 'product' input variable but one was not set!")

        if not major_version:
            raise ProcessorError(
                "Expected an 'major_version' input variable but one was not set!")

        self.output('Searching for patches for:  {product} {major_version}'.format(product=product, major_version=major_version))

        # Build the URLs
        lookupURL = "https://knowledge.autodesk.com/autodesk-downloads-finder/search?p={product}&v={major_version}".format(product=product, major_version=major_version)
        pattern = "https://up.autodesk.com/{major_version}/{product}".format(product=product, major_version=major_version)

        # Look up the product and major_version
        response = self.download(lookupURL)

        if response:
            # Load the JSON Response
            json_data = json.loads(response)

            patches = {}
            if json_data.get("Hotfixes"):
                for hotfix in json_data.get("Hotfixes").get("docs"):
                    patches[hotfix.get("published")] = hotfix.get("link")

            if json_data.get("Service Packs"):
                for hotfix in json_data.get("Service Packs").get("docs"):
                    patches[hotfix.get("published")] = hotfix.get("link")

            # Get the latest patch
            # The "published" key is the epoch time of the release date, so simply get the largest number
            search_url = patches[sorted(patches.keys())[-1]]

            # Return results
            self.env["search_url"] = search_url
            self.output("URL URL: {}".format(self.env["search_url"]))
            self.env["search_pattern"] = pattern
            self.output("Search Pattern: {}".format(self.env["search_pattern"]))

        else:
            raise ProcessorError("Unable to find an update for the provided product and major_version.")

if __name__ == "__main__":
    processor = AutoDeskPatchProcessor()
    processor.execute_shell()
