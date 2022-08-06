#!/usr/local/autopkg/python
#
# Copyright 2019 Zack Thompson (MLBZ521)
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

import xml.etree.ElementTree as ET

from autopkglib import ProcessorError, URLGetter


__all__ = ["MaplePatchURLProvider"]


class MaplePatchURLProvider(URLGetter):

    """This processor finds the URL for the latest patch of the supplied major
     version of Maple."""

    description = __doc__
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


    def main(self):

        # Define variables
        major_version = self.env.get("major_version")

        if not major_version:
            raise ProcessorError("Expected an 'major_version' input variable but none is set!")
        else:
            self.output(f"Searching for patches for major version:  {major_version}", verbose_level=1)

        # To get the UUID:
        # Install Maple > open the file:
        # /Library/Frameworks/Maple.framework/Versions/<VERSION>/update/update.ini
        # The UUID is listed in the url variable
        # Do note that each release/upgrade for each major version has a different UUID, but shouldn't be a big deal

        if major_version == "2022":
            uuid = "17b89e08-f3f1-4f53-b58b-e73d0c030d25" # This is technically 2022.1
        if major_version == "2021":
            uuid = "1281b851-d7ce-4c6d-af1f-81d4549db8fc" # This is technically 2021.1
        elif major_version == "2020":
            uuid = "80c01c3a-4a87-4421-95f3-6511001dc329" # This is technically 2020.1
        elif major_version == "2019":
            uuid = "a8326412-07ae-4dbb-a727-6bd0ca623bbf"
        elif major_version == "2018":
            uuid = "11fd3561-032e-4750-846a-993353f154c2"
        elif major_version == "2017":
            uuid = "6251ab90-135f-4e20-b147-7fbdf895dcb9"
        elif major_version == "2016":
            uuid = "f880ced0-a1cf-422f-b782-9decffa5f2c7"
        else:
            raise ProcessorError(f"Unable to lookup patches for major version:  {major_version}.")

        # Build the URL
        lookupURL = f"http://update.maplesoft.com/update.php?uuid={uuid}"

        # Look up the model
        xml = self.download(lookupURL)

        if xml:
            # self.output(f"Results:  \n{xml}, verbose_level=4)"
    
            # Import xml string into an object
            tree = ET.fromstring(xml)

            # Get the desired elements
            version = tree.findtext("./version")
            baseURL = tree.findtext("./downloadLocationList/downloadLocation/url")
            filename = tree.findtext("./platformFileList/platformFile/filename")

            # Build download url
            url = f"{baseURL}/{filename}"

            # Return results
            self.env["url"] = url
            self.output(f"Download URL: {self.env['url']}", verbose_level=2)
            self.env["version"] = version
            self.output(f"version: {self.env['version']}", verbose_level=2)

        else:
            raise ProcessorError("Unable to find an update for the provided version.")


if __name__ == "__main__":
    PROCESSOR = MaplePatchURLProvider()
    PROCESSOR.execute_shell()
