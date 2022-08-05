#!/usr/local/autopkg/python
#
# Copyright 2021 Zack T (mlbz521)
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

from __future__ import absolute_import, print_function

import json
import re

from html.parser import HTMLParser

from autopkglib import Processor, ProcessorError, URLGetter


__all__ = ["XeroxPrintDriverProcessor"]


class XeroxPrintDriverProcessor(URLGetter):
    """This processor finds the URL for the desired Xerox print driver version.
    """

    input_variables = {
        "model": {
            "required": True,
            "description": "The model of the Xerox Printer to search for."
                            "(Note:  Spaces will be escaped.)",
        },
        "downloadType": {
            "required": False,
            "description": "The type package type desired, some examples are: "
                            " - macOS Print and Scan Driver Installer (default)"
                            " - ICA Scan USB Driver"
                            " - IMAC CA Scan USB Driver"
                            " - TWAIN Scan Driver"
                            "(The provided string is used to search for the desired download.  "
                            "Regex is used to find matching items, so the supplied option can "
                            "be a generic string, without specific version information to "
                            "download any available download for the specified model.)"
        },
        "osVersion": {
            "required": False,
            "description": "The OS version to search against."
                            "Default:  'x11' (i.e. Big Sur).",
        }
    }
    output_variables = {
        "url": {
            "description": "Returns the url to download."
        }
    }

    description = __doc__


    def main(self):
        """Main process."""

        class MyHTMLParser(HTMLParser):

            def __init__(self):
                HTMLParser.__init__(self)
                self.url_path = ""

            def handle_starttag(self, tag, attributes):

                # Only looking for 'a' elements
                if tag != "a":
                    return

                # If an 'a' element, loop through the attributes
                for name, value in attributes:

                    # Is this the value we're looking for?
                    if name == "aria-label" and re.search("Download: {}.*".format(downloadType), value):

                        # Loop back through and get the 'href' path
                        for name, value in attributes:

                            if name == 'onclick':
                                self.url_path = re.search("https:\/\/.*[.]\w\w\w", value)[0]
                                return


        # Define variables
        input_model = self.env.get('model')
        self.output('Searching for:  {}'.format(input_model))
        downloadType = self.env.get('downloadType', 'macOS Print and Scan Driver Installer')
        osVersion = self.env.get('osVersion', 'x11')
        parser = MyHTMLParser()

        # Build the headers
        headers = {
            "Authorization": "Bearer xx223a56be-26b1-4b0f-a1ea-39a56e8343e8",
            "Content-Type": "application/x-www-form-urlencoded; charset=\"UTF-8\""
        }

        # Build the required curl switches
        curl_opts = [
            "--url", "https://platform.cloud.coveo.com/rest/search/v2?organizationId=xeroxcorporationproductiono2r4c199",
            "--request", "POST",
            "--data", '&referrer=https://www.support.xerox.com/&aq=@producttagname=="{}"&cq=@source=="Xerox Support"&tab=DriversDownloads&pipeline=XeroxPublic&context={{"locale":"en-us","lang":"en","fulllang":"en-us","product":"","supportlang":"English","supportshortlang":"en"}}&fieldsToInclude=[]'.format(input_model)
        ]

        try:
            # Initialize the curl_cmd, add the curl options, and execute curl
            curl_cmd = self.prepare_curl_cmd()
            self.add_curl_headers(curl_cmd, headers)
            curl_cmd.extend(curl_opts)
            model_lookup = self.download_with_curl(curl_cmd)

            self.output("Model lookup response:  {}".format(model_lookup), verbose_level=4)

        except:
            raise ProcessorError("Failed to match the provided model:  {}".format(input_model))

        try:
            # Load the JSON Response
            json_data = json.loads(model_lookup)

            for result in json_data['results']:
                if re.match(r".*Drivers & Downloads", result.get('title')):
                    model_downloads_page = result.get('clickUri')
                    self.output("Model downloads page:  {}".format(model_downloads_page), verbose_level=2)

        except:
            raise ProcessorError("Failed to find a model url in the results!")

        # Build url
        os_version_lookup_url = '{}?platform=macOS{}'.format(model_downloads_page, osVersion)
        self.output("OS version lookup URL:  {}".format(os_version_lookup_url), verbose_level=2)

        try:

            # Perform lookup to get available download types
            pageContent = self.download(os_version_lookup_url, text=True)
            self.output("Page Content:  {}".format(pageContent), verbose_level=4)

            # Parse the HTML for the desired data
            parser.feed(pageContent)
            download_path = parser.url_path

        except:
            raise ProcessorError("Unable to find available downloads or download types.")

        if download_path:
            # Return results
            self.env["url"] = download_path
            self.output("Download URL: {}".format(self.env["url"]))

        else:
            raise ProcessorError("Failed to find a matching download type for the provided model.")


if __name__ == "__main__":
    processor = XeroxPrintDriverProcessor()
    processor.execute_shell()
