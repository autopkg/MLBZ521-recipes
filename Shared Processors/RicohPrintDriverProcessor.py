#!/usr/bin/env python
#
# Copyright 2022 Zack Thompson (mlbz521)
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
import os
import sys

from html.parser import HTMLParser

from autopkglib import ProcessorError, URLGetter

if not os.path.exists("/Library/AutoPkg/Selenium"):
    raise ProcessorError("Selenium is required for this recipe!  "
    "Please review my Shared Processors README.")

sys.path.insert(0, "/Library/AutoPkg/Selenium")
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

sys.path.insert(0, f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Shared Processors")
from SeleniumWebScrapper import WebEngine


__all__ = ["RicohPrintDriverProcessor"]


class RicohPrintDriverProcessor(URLGetter):

    """This processor finds the download URL for Ricoh print driver."""

    input_variables = {
        "model": {
            "required": True,
            "description": (
                "The official model name of the Ricoh Printer to search for."
            )
        },
        "os_version": {
            "required": False,
            "description": (
                "The OS version to search against.",
                "Default:  'Big Sur"
            )
        },
        "web_driver": {
            "required": False,
            "description": (
                "The web driver engine to use.  Only Chrome is supported at this time, "
                "but support for additional web drivers can be added.",
                "Default:  Chrome"
            )
        },
        "web_driver_path": {
            "required": False,
            "description": (
                "The path to the web driver.  _If_ it is not in your system $PATH.",
                "Default:  $PATH"
            )
        },
        "web_driver_binary_location": {
            "required": False,
            "description": (
                "The path to the browser's binary.  Defaults to using Chromium.",
                "Default:  /Applications/Chromium.app/Contents/MacOS/Chromium"
            )
        }
    }
    output_variables = {
        "url": {
            "description": "Returns the url to download."
        }
    }

    description = __doc__


    class MyHTMLParser(HTMLParser):

        def __init__(self):
            HTMLParser.__init__(self)
            self.url_path = ""
            self.search_match = ""

        def handle_starttag(self, tag, attributes):

            if not self.url_path and tag == "a":

                for name, value in attributes:

                    if name == 'onclick':

                        self.search_match = re.search(
                            r".*(https:\/\/support[.]ricoh[.]com/bb/html/.+[.]htm)", value)

                        if self.search_match:

                            self.url_path = self.search_match.group(1)
                            break


    def main(self):
        """Do the main thing."""

        # Define variables
        model = self.env.get('model')
        os_version = self.env.get("os_version", "Big Sur")
        web_driver = self.env.get("web_driver", "Chrome")
        web_driver_path = self.env.get("web_driver_path")
        web_driver_binary_location = self.env.get("web_driver_binary_location")

        if not model:
            raise ProcessorError(
                "Expected an 'model' input variable but one was not set!")

        self.output(f'Searching for printer model:  {model}')

        if os_version == "Big Sur":
            os_version_keycode="120905"
        elif os_version == "Catalina":
            os_version_keycode="119803"
        elif os_version == "Mojave":
            os_version_keycode="118404"
        elif os_version == "High Sierra":
            os_version_keycode="116504"
        elif os_version == "Sierra":
            os_version_keycode="115063"
        else:
            raise ProcessorError("Unknown OS Version requested.")

        # Build the URL
        model_escaped = re.sub(r"\s", "_", model)
        lookupURL = f"https://www.ricoh-usa.com/Common/DownloadSearch/LoadSearchDetails?searchfor={model_escaped}&isBrochure=true&isDrivers=true&isManual=true&endecaURL=DownloadSearch&endecaSearchPage=SearchResultPage&hdnmobiledriverlink=&ismobile=false&hdnEmptyResultText=No+results+found.&hdnEmptySearchResultText1=Your+search+did+not+yield+any+results.&hdnEmptySearchResultText2=did+not+return+any+models.&CategorySelect=Category&SubCategorySelect=Sub+Category&ModelSelect=Model&DriverLabel=DRIVER&DriversLabel=DRIVERS&ManualsLabel=MANUAL"

        # Look up the product
        response = self.download(lookupURL)

        # Encode/decode the response into valid HTML
        html = (response).decode("utf-8").encode().decode('unicode-escape')

        if html:

            try:
                # Parse the HTML for the desired data
                parser = self.MyHTMLParser()
                parser.feed(html)

                if not parser.url_path:
                    raise ProcessorError("Unable to find available identify the driver download page.")

                self.output(f'Driver download page URL:  {parser.url_path}')

            except:
                raise ProcessorError("Unable to find available downloads.")

        with WebEngine(
            engine=web_driver, binary=web_driver_binary_location, path=web_driver_path, parent=self) as web_engine:

            try:
                web_engine.get(parser.url_path)

            except:
                raise ProcessorError("Failed to access the driver download page.")

            try:
                section_MacOSX = '//*[@id="os-driver-list"]/div[4]/div/div/div[1]/a'
                # Open the "Drivers & Download" section
                WebDriverWait(web_engine, timeout=10).until(
                    lambda d: d.find_element_by_xpath(section_MacOSX)
                )
                web_engine.find_element_by_xpath(section_MacOSX).click()
                self.output("Selected operating system section labled \"Mac OS X\"", verbose_level=3)

            except:
                raise ProcessorError("Failed to find and open the operating system section labled \"Mac OS X\".")

            try:
                # Select the desired OS Version
                xpath_os_version = f'//*[@id="os-driver-list"]/div[4]/div/div/div[2]//a[@keycode={os_version_keycode}]'

                WebDriverWait(web_engine, timeout=10).until(
                    lambda d: d.find_element_by_xpath(xpath_os_version)
                )
                presence_of_element_located(xpath_os_version)

                section_selected_os_version = web_engine.find_element_by_xpath(xpath_os_version)
                section_selected_os_version.click

                self.output(f"Selected the section for OS Version:  {os_version}", verbose_level=3)

            except:
                raise ProcessorError("Failed to select the desired OS Version")

            try:
                # Get the hyperlink for the driver download file
                download_url = section_selected_os_version.find_element_by_xpath(
                    '//*[@id="os-driver-list"]/div[4]/div/div/div[2]/div[1]/div/div/div[2]/div/div/div/div/div/div[1]/p[2]/a').get_attribute("href"
                )

            except:
                raise ProcessorError(
                    "Failed to find and collect the download url from the download button.")

        if not download_url:
            raise ProcessorError("Failed to find a matching download type for the provided model.")

        # Return results
        self.env["url"] = download_url
        self.output(f'Download URL: {self.env["url"]}', verbose_level=1)


if __name__ == "__main__":
    processor = RicohPrintDriverProcessor()
    processor.execute_shell()
