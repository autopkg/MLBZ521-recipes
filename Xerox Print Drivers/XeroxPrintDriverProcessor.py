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
                            "(The provided string is searched in the web page.  "
                            "In the future, additional logic can likely be provide "
                            "to expand functionality if desired.)"
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

        # Define variables
        input_model = self.env.get('model')
        self.output('Searching for:  {}'.format(input_model))
        downloadType = self.env.get('downloadType', 'macOS Print and Scan Driver Installer')
        osVersion = self.env.get('osVersion', '10_15')

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
            lookupURL = '{downloads_uri}?operatingSystem=macOS{osVersion}'.format(downloads_uri=downloads_uri, osVersion=osVersion)

            # Perform second lookup to get available download types
            pageContent = self.download(lookupURL, text=True)

            # Find the download type requested
            downloadPageURL = None
            for line in pageContent.split('\n'):
                if downloadType in line:
                    downloadPageURL = line.strip()
                    self.output('Download Type URL:  {}'.format(downloadPageURL))

        except:
            raise ProcessorError("Failed to find the downloadType in the results!")

        try:
            # Get the contentId from the found line
            contentID = re.findall(r'contentId=(\d*)', downloadPageURL)
            # self.output("contentID:  {}".format(contentID))

            # Build download url
            downloadsURL = re.sub(r'downloads', 'file-redirect', downloads_uri)
            # self.output('Download URL:  {}'.format(downloadsURL))
            url = '{downloadsURL}?operatingSystem=macOS{osVersion}&fileLanguage=en&contentId={downloadID}'.format(downloadsURL=downloadsURL, osVersion=osVersion, downloadID=contentID[0])

            # Return results
            self.env["url"] = url
            self.output("Download URL: {}".format(self.env["url"]))

        except:
            raise ProcessorError("Unable to build a download url based on the parameters provided.")

if __name__ == "__main__":
    processor = XeroxPrintDriverProcessor()
    processor.execute_shell()
