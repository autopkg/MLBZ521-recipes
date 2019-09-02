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
import subprocess
import sys

import requests  # Use requests if available

from autopkglib import Processor, ProcessorError

try:
    from urllib import request as urllib  # For Python 3
except ImportError:
    import urllib  # For Python 2

__all__ = ["XeroxPrintDriverProcessor"]

class XeroxPrintDriverProcessor(Processor):

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
                            " - macOS Common Print Driver Installer (default)"
                            " - IMAC CA Scan USB Driver"
                            " - ICA Scan Driver"
                            " - TWAIN Scan Driver"
                            "(The provided string is searched in the web page.  "
                            "In the future, additional logic can likely be provide "
                            "to expand functionality if desired.)"
        },
        "osVersion": {
            "required": False,
            "description": "The OS version to search against, match the "
                            "format of '10_14', which is the default.",
        }
    }
    output_variables = {
        "url": {
            "description": "Returns the url to download."
        }
    }

    description = __doc__

    def main(self):

        def webContent(url):
            """A helper function for getting the contents of a web page.
            Args:
                url:  The url of the web page.
            Returns:
                stdout:  Text content of the web page.
            """
            try:
                response = requests.get(url)
                return response.content
            except:
                sys.exc_clear()

                try:
                    response = urllib.urlopen(url)
                    return response.read()
                except BaseException:
                    # If still fails (running on macOS 10.12 or older), resort to using curl
                    sys.exc_clear()

                    # Build the command.
                    curl_cmd = '/usr/bin/curl --silent --show-error --no-buffer --fail --speed-time 30 --url "{}"'.format(url)
                    try:
                        response = subprocess.check_output(curl_cmd, shell=True)
                        return response
                    except subprocess.CalledProcessError as error:
                        print(('Return code:  {}'.format(error.returncode)))
                        print(('Result:  {}'.format(error)))


        # Define variables
        input_model = self.env.get('model')
        model = re.sub(r'\s', '%20', input_model)
        self.output('Searching for:  {}'.format(model))
        downloadType = self.env.get('downloadType', 'macOS Common Print Driver Installer')
        osVersion = self.env.get('osVersion', '10_14')

        # Build the URL
        lookupURL = 'https://www.xerox.com/en-us/d-api/proxy/support-proxy.php?mode=results&search={model}&callback=handleSearchClickResponse'.format(model=model)

        # Look up the model
        dirty_json = webContent(lookupURL)

        # Clean up results so we can parse as a json object
        dirty_json = re.sub(r'^\/\*\*\/ typeof handleSearchClickResponse === \'function\' && handleSearchClickResponse\(', '', dirty_json)
        clean_json = re.sub(r'\);$', '', dirty_json)
        json_data = json.loads(clean_json)
        # self.output('Search results:  {}'.format(json_data))

        for link in json_data['results'][0]['links']:
            if link['title'] == 'Drivers & Downloads':
                downloadsURL = link['url']
                self.output('Found Downloads Link:  {}'.format(downloadsURL))

        # Build url
        lookupURL2 = 'https://www.support.xerox.com{crumbs}?operatingSystem=macOS{osVersion}'.format(crumbs=downloadsURL, osVersion=osVersion)

        # Perform second lookup to get available download types
        pageContent = webContent(lookupURL2)

        # Find the download type requested
        for line in pageContent.split('\n'):
            if downloadType in line:
                downloadPageURL = line.strip()
                # self.output('Download Type URL:  {}'.format(downloadPageURL))

        if downloadPageURL:
            # Get the contentId from the found line
            contentID = re.findall(r'contentId=(\d*)', downloadPageURL)

            # Build download url
            crumbs = re.sub(r'downloads', 'file-redirect', downloadsURL)
            url = 'https://www.support.xerox.com{crumbs}?operatingSystem=macOS{osVersion}&fileLanguage=en&contentId={downloadID}'.format(crumbs=crumbs, osVersion=osVersion, downloadID=contentID[0])
            # self.output('Download URL:  {}'.format(downloadURL))

            # Return results
            self.env["url"] = url
            self.output("Download URL: {}".format(self.env["url"]))

        else:
            raise ProcessorError("Unable to find a url based on the parameters provided.")

if __name__ == "__main__":
    processor = XeroxPrintDriverProcessor()
    processor.execute_shell()
