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

import re
import os
import sys
import time

from autopkglib import Processor, ProcessorError

if not os.path.exists("/Library/AutoPkg/Selenium"):
    raise ProcessorError("Selenium is required for this recipe!  "
        "Please review my Shared Processors README.")

sys.path.insert(0, "/Library/AutoPkg/Selenium")
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support.expected_conditions import presence_of_element_located

sys.path.insert(0, f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Shared Processors")
from SeleniumWebScrapper import WebEngine


__all__ = ["PharosURLProvider"]


class PharosURLProvider(Processor):

    """This processor finds the download URL for Pharos Popup Client."""

    input_variables = {
        "downloads_page": {
            "required": False,
            "description": (
                "The downloads page to search on."
                "Default:  https://community.pharos.com/s/article/Macintosh-Updates-For-Uniprint"
            )
        },
        "prefix_dl_url": {
            "required": False,
            "description": (
                "The prefix of the downloads url to match."
                "Default:  https://pharos.com/support/downloads/mac/Mac OS X Popup"
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


    def main(self):
        """Do the main thing."""

        # Define variables
        downloads_page = self.env.get("downloads_page", 
            "https://community.pharos.com/s/article/Macintosh-Updates-For-Uniprint")
        prefix_dl_url = self.env.get("prefix_dl_url", 
            "https://pharos.com/support/downloads/mac/Mac OS X Popup")
        prefix_dl_url = re.sub(r"\s", "%20", prefix_dl_url)
        web_driver = self.env.get("web_driver", "Chrome")
        web_driver_path = self.env.get("web_driver_path")
        web_driver_binary_location = self.env.get("web_driver_binary_location")

        # self.output(f"downloads_page:  {downloads_page}", verbose_level=3)
        # self.output(f"prefix_dl_url:  {prefix_dl_url}", verbose_level=3)

        with WebEngine(
            engine=web_driver, binary=web_driver_binary_location, path=web_driver_path, parent=self) as web_engine:

            try:
                web_engine.get(downloads_page)
                time.sleep(2)
            except:
                raise ProcessorError("Failed to access the download page.")

            try:
                WebDriverWait(web_engine, timeout=10).until(
                    lambda d: d.find_elements(By.LINK_TEXT, "Download")
                )
                download_links = web_engine.find_elements(By.LINK_TEXT, "Download")
            except:
                raise ProcessorError("Failed to find and open the operating "
                    "system section labeled \"Mac OS X\".")

            try:
                for link in download_links:
                    if re.match(prefix_dl_url, link.get_attribute("href")):
                        download_url = link.get_attribute("href")
                        version = re.match(r".+(\d+\.\d+\.\d+).+", download_url)[1]

            except:
                raise ProcessorError(
                    "Failed to find and collect the download url from the download link.")

        if not download_url:
            raise ProcessorError("Failed to find a matching download type for the provided model.")

        if not version:
            raise ProcessorError("Failed to identify the version of the download.")

        self.env["url"] = download_url
        self.output(f"Download URL: {self.env['url']}", verbose_level=1)
        self.env["version"] = version
        self.output(f"Version: {self.env['version']}", verbose_level=1)


if __name__ == "__main__":
    PROCESSOR = PharosURLProvider()
    PROCESSOR.execute_shell()
