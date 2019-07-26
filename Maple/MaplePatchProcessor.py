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

import requests # Use requests if available
try:
    from urllib import request as urllib  # For Python 3
except ImportError:
    import urllib  # For Python 2
import subprocess
import sys
import xml.etree.ElementTree as ET
from autopkglib import Processor, ProcessorError

__all__ = ["MaplePatchProcessor"]

class MaplePatchProcessor(Processor):

    """This processor finds the URL for the desired Xerox print driver version.
    """

    input_variables = {
        "major_version": {
            "required": True,
            "description": "Which Maples Major Version to look for available patches.",
        }
    }
    output_variables = {
        "url": {
            "description": "Returns the url to download."
        },
        "version": {
            "description": "Returns the version number."
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
                except Exception:
                    # If still fails (running on macOS 10.12 or older), resort to using curl
                    sys.exc_clear()

                    # Build the command.
                    curl_cmd = '/usr/bin/curl --silent --show-error --no-buffer --fail --speed-time 30 --url "{}"'.format(url)
                    try:
                        response = subprocess.check_output(curl_cmd, shell=True)
                        return response
                    except subprocess.CalledProcessError as error:
                        print('Return code:  {}'.format(error.returncode))
                        print('Result:  {}'.format(error))


        # Define variables
        major_version = self.env.get('major_version')
        if not major_version:
            raise ProcessorError(
                "Expected an 'major_version' input variable but none is set!")
        else:
            self.output('Searching for patches for major version:  {}'.format(major_version))

        if major_version == "2019":
            uuid = 'a8326412-07ae-4dbb-a727-6bd0ca623bbf'
        elif major_version == "2018":
            uuid = '11fd3561-032e-4750-846a-993353f154c2'
        elif major_version == "2017":
            uuid = '6251ab90-135f-4e20-b147-7fbdf895dcb9'
        elif major_version == "2016":
            uuid = 'f880ced0-a1cf-422f-b782-9decffa5f2c7'
        else:
            raise ProcessorError('Unable to lookup patches for major version:  {major_version}.'.format(major_version=major_version))

        # Build the URL
        lookupURL = 'http://update.maplesoft.com/update.php?uuid={uuid}'.format(uuid=uuid)

        # Look up the model
        xml = webContent(lookupURL)
        # self.output('Results:  \n{}'.format(xml))

        if xml:
            # Import xml string into an object
            tree = ET.fromstring(xml)

            # Get the desired elements
            version = tree.findtext('./version')
            baseURL = tree.findtext('./downloadLocationList/downloadLocation/url')
            filename = tree.findtext('./platformFileList/platformFile/filename')

            # Build download url
            url = '{baseURL}/{filename}'.format(baseURL=baseURL, filename=filename)

            # Return results
            self.env["url"] = url
            self.output("Download URL: {}".format(self.env["url"]))
            self.env["version"] = version
            self.output("version: {}".format(self.env["version"]))

        else:
            raise ProcessorError("Unable to find an update for the provided version.")

if __name__ == "__main__":
    processor = MaplePatchProcessor()
    processor.execute_shell()
