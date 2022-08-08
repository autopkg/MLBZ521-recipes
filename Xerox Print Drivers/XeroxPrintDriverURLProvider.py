#!/usr/local/autopkg/python
#
# Copyright 2022 Zack Thompson (MLBZ521)
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
import re

from html.parser import HTMLParser

from autopkglib import ProcessorError, URLGetter


__all__ = ["XeroxPrintDriverURLProvider"]


class XeroxPrintDriverURLProvider(URLGetter):
    """This processor finds the URL for the desired Xerox print driver version.
    """

    description = __doc__
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
        "os_version": {
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


    def main(self):
        """Main process."""

        class MyHTMLParser(HTMLParser):

            def __init__(self):
                HTMLParser.__init__(self)
                self.url_path = ""

            def handle_starttag(self, tag, attributes):

                # Only looking for "a" elements
                if tag != "a":
                    return

                # If an "a" element, loop through the attributes
                for name, value in attributes:

                    # Is this the value we're looking for?
                    if name == "aria-label" and re.search(f"Download: {download_type}.*", value):

                        # Loop back through and get the "href" path
                        for name, value in attributes:

                            if name == "onclick":
                                self.url_path = re.search("https:\/\/.*[.]\w\w\w", value)[0]
                                return


        # Define variables
        input_model = self.env.get("model")
        self.output(f"Searching for:  {input_model}")
        download_type = self.env.get("download_type", "macOS Print and Scan Driver Installer")
        os_version = self.env.get("os_version", "x11")
        parser = MyHTMLParser()

        # Build the headers
        headers = {
            "Authorization": "Bearer xx223a56be-26b1-4b0f-a1ea-39a56e8343e8",
            "Content-Type": "application/x-www-form-urlencoded; charset=\"UTF-8\""
        }

        # Build the required curl switches
        curl_opts = [
            "--url", 
            "https://platform.cloud.coveo.com/rest/search/v2?organizationId=xeroxcorporationproductiono2r4c199",
            "--request", "POST",
            "--data", 
            f'&referrer=https://www.support.xerox.com/&aq=@producttagname=="{input_model}"&cq=@source=="Xerox Support"&tab=DriversDownloads&pipeline=XeroxPublic&context={{"locale":"en-us","lang":"en","fulllang":"en-us","product":"","supportlang":"English","supportshortlang":"en"}}&fieldsToInclude=[]'
        ]

        try:
            # Initialize the curl_cmd, add the curl options, and execute curl
            curl_cmd = self.prepare_curl_cmd()
            self.add_curl_headers(curl_cmd, headers)
            curl_cmd.extend(curl_opts)
            model_lookup = self.download_with_curl(curl_cmd)

            self.output(f"Model lookup response:  {model_lookup}", verbose_level=4)

        except:
            raise ProcessorError(f"Failed to match the provided model:  {input_model}")

        try:
            # Load the JSON Response
            json_data = json.loads(model_lookup)

            for result in json_data["results"]:
                if re.match(r".*Drivers & Downloads", result.get("title")):
                    model_downloads_page = result.get("clickUri")
                    self.output(f"Model downloads page:  {model_downloads_page}", verbose_level=2)

        except:
            raise ProcessorError("Failed to find a model url in the results!")

        # Build url
        os_version_lookup_url = f"{model_downloads_page}?platform=macOS{os_version}"
        self.output(f"OS version lookup URL:  {os_version_lookup_url}", verbose_level=2)

        try:

            # Perform lookup to get available download types
            page_content = self.download(os_version_lookup_url, text=True)
            self.output(f"Page Content:  {page_content}", verbose_level=4)

            # Parse the HTML for the desired data
            parser.feed(page_content)
            download_path = parser.url_path

        except:
            raise ProcessorError("Unable to find available downloads or download types.")

        if download_path:
            # Return results
            self.env["url"] = download_path
            self.output(f"Download URL: {self.env['url']}")

        else:
            raise ProcessorError("Failed to find a matching download type for the provided model.")


if __name__ == "__main__":
    PROCESSOR = XeroxPrintDriverURLProvider()
    PROCESSOR.execute_shell()
