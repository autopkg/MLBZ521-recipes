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

from __future__ import absolute_import, print_function

from html.parser import HTMLParser
import json
import re

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
            "description": "The OS version to search against, match the "
                            "format of '10_15', which is the default.",
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

                            if name == 'href':
                                self.url_path = value
                                return


        # Define variables
        input_model = self.env.get('model')
        self.output('Searching for:  {}'.format(input_model))
        downloadType = self.env.get('downloadType', 'macOS Print and Scan Driver Installer')
        osVersion = self.env.get('osVersion', '10_15')
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
            # Initialize the curl_cmd, add the curl options, and execute the curl
            curl_cmd = self.prepare_curl_cmd()
            self.add_curl_headers(curl_cmd, headers)
            curl_cmd.extend(curl_opts)
            response_token = self.download_with_curl(curl_cmd)

        except:
            raise ProcessorError("Failed to match the provided model:  {}".format(input_model))


        try:
            # Load the JSON Response
            json_data = json.loads(response_token)

            for result in json_data['results']:
                if re.match(r".*Drivers & Downloads", result.get('title')):
                    downloads_uri = result.get('clickUri')
                    # self.output("downloads_uri:  {}".format(downloads_uri))

        except:
            raise ProcessorError("Failed to find a model url in the results!")

        try:
            # Build url
            lookupURL = '{downloads_uri}?platform=macOS{osVersion}'.format(downloads_uri=downloads_uri, osVersion=osVersion)
            # self.output("lookupURL:  {}".format(lookupURL))

            # Perform second lookup to get available download types
            pageContent = self.download(lookupURL, text=True)

            # Parse the HTML for the desired data
            parser.feed(pageContent)

            download_path = parser.url_path
            # print("download_path:  {}".format(download_path))

            if download_path:
                url = "https://www.support.xerox.com{}".format(download_path)

                # Return results
                self.env["url"] = url
                self.output("Download URL: {}".format(self.env["url"]))

            else:
                raise ProcessorError("Unable to build a download url based on the parameters provided.")

        except:
            raise ProcessorError("Unable to build a download url based on the parameters provided.")

if __name__ == "__main__":
    processor = XeroxPrintDriverProcessor()
    processor.execute_shell()
