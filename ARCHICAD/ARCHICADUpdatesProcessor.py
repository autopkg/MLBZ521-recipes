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

import re
import requests
import json
from HTMLParser import HTMLParser
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

        # Define some variables
        major_version = self.env.get("major_version")
        localization = self.env.get("localization")
        relase_type = self.env.get("relase_type")

        class MyHTMLParser(HTMLParser):
            # Initializing list
            lsData = list()

            # HTML Parser Methods
            def handle_data(self, data):
                self.lsData.append(data)

        response = requests.get('https://www.graphisoft.com/downloads/archicad/updates/')
        parser = MyHTMLParser()
        parser.feed(response.content)

        for data in parser.lsData:
            json_text = re.search(r'.*\}\(\[.*$', data, flags=re.DOTALL | re.MULTILINE)
            if json_text:
                content = data

        content_Split1 = re.split(r'\}\(', content)  # Split contents at:  }(
        content_Split2 = re.split(r'\);', content_Split1[1])  # Split contents at:  \;
        clean_Spacing = re.sub(r'^[\s]*', '', content_Split2[0], flags=re.MULTILINE)  # Strip some leading spaces
        escape_Double_Quotes = re.sub(r'"', '\\"', clean_Spacing, flags=re.MULTILINE)  # Escape existing double quotes
        replace_Single_Quotes = re.sub(r'\'', '"', escape_Double_Quotes, flags=re.MULTILINE)  # Replace existing single quotes with double quotes
        braces_New_Lines = re.sub(r'^{\s?\b', '{\n', replace_Single_Quotes, flags=re.MULTILINE)  # At all open braces '{', insert a new line
        add_New_Lines = re.sub(r'",[^\n]\b', '",\n', braces_New_Lines, flags=re.MULTILINE)  # Add new lines where needed
        quote_Keys = re.sub(r'^(\w*\b)', r'"\1"', add_New_Lines, flags=re.MULTILINE)  # Quote the keys
        remove_Extra_Commas = re.sub(r',(\s*(]|}))', r'\1', quote_Keys, flags=re.MULTILINE)  # Remove extra commas

        valid_JSON = json.loads(remove_Extra_Commas)
        available_builds = {}

        for json_Object in valid_JSON:
            if json_Object.get('version') == '22':
                if json_Object.get('localization') == 'USA':
                    if json_Object.get('type') == 'FULL':
                        for details in json_Object['downloadLinks']:
                            if details.get('platform') == 'mac':
                                available_builds[json_Object.get('build')] = details['url']

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
