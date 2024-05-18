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

import os
import sys
import json

from autopkglib import ProcessorError, URLGetter

if not os.path.exists("/Library/AutoPkg/Selenium"):
    raise ProcessorError("Selenium is required for this recipe!  "
    "Please review my Shared Processors README.")

sys.path.insert(0, "/Library/AutoPkg/Selenium")
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

sys.path.insert(0, f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Shared Processors")
from SeleniumWebScrapper import WebEngine


__all__ = ["RicohPrintDriverURLProvider"]


class RicohPrintDriverURLProvider(URLGetter):
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
            "description": "The OS version to search against.",
            "default":  "latest"
        },
        "web_driver": {
            "required": False,
            "description": (
                "The web driver engine to use.  Only Chrome is supported at this time, "
                "but support for additional web drivers can be added."
            ),
            "default":  "Chrome"
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
        },
        "WEB_ENGINE_HEADLESS": {
            "required": False,
            "type": bool,
            "description": (
                "Whether to run the web engine headless or not.  ",
                "This is specifically for troubleshooting purposes.",
                "Default:  False"
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
        if not (model := self.env.get('model')):
            raise ProcessorError("Expected a 'model' input variable but one was not set!")
        self.output(f'Searching for printer model:  {model}')

        os_version = self.env.get("os_version", "latest")
        web_driver = self.env.get("web_driver", "Chrome")
        web_driver_path = self.env.get("web_driver_path")
        web_driver_binary_location = self.env.get("web_driver_binary_location")
        web_engine_headless = bool(self.env.get("WEB_ENGINE_HEADLESS"))

        if os_version in ["Ventura", "latest", "", None]:
            os_version_keycode="122825"
        elif os_version == "Monterey":
            os_version_keycode="121887"
        elif os_version == "Big Sur":
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

        # Build the required curl switches
        curl_opts = [
            "--url", "https://www.ricoh-usa.com/api/search",
            "--data-raw",
            json.dumps(
                {"requestState":
                    {
                        "current":1,"filters":[],"resultsPerPage":100,"searchTerm":model,
                        "sortDirection":"","sortField":"","sortList":[]
                    },
                    "queryConfig":{
                        "filters": [
                            {
                                "field": "locale",
                                "values": ["en-US"],
                                "type": "all"
                            }
                        ],
                        "result_fields":
                            {"Gen_Linked_Driver_Drivers":{"raw":{}}}
                    }
                }
            )
        ]
        headers = {"content-type": "application/json"}
        try:
            # Initialize the curl_cmd, add the curl options, and execute curl
            curl_cmd = self.prepare_curl_cmd()
            self.add_curl_headers(curl_cmd, headers)
            curl_cmd.extend(curl_opts)
            result = self.download_with_curl(curl_cmd)
        except:
            raise ProcessorError("Failed to query the Ricoh API.")

        try:
            drive_page_url = json.loads(
                result).get("results")[0].get("Gen_Linked_Driver_Drivers").get("raw")
        except json.JSONDecodeError as error:
            raise ProcessorError("Failed to parse the response from the Ricoh API.") from error

        with WebEngine(
            engine=web_driver, binary=web_driver_binary_location, 
            path=web_driver_path, headless=web_engine_headless, parent=self
        ) as web_engine:

            try:
                web_engine.get(drive_page_url)
            except:
                raise ProcessorError("Failed to access the driver download page.")

            try:
                section_MacOSX = '//*[@id="os-driver-list"]/div[4]/div/div/div[1]/a'
                # Open the "Drivers & Download" section
                WebDriverWait(web_engine, timeout=10).until(
                    lambda d: d.find_element(By.XPATH, section_MacOSX)
                )
                web_engine.find_element(By.XPATH, section_MacOSX).click()
                self.output("Selected operating system section labeled \"Mac OS X\"", verbose_level=3)
            except:
                raise ProcessorError("Failed to find and open the operating system section labeled \"Mac OS X\".")

            try:
                # Select the desired OS Version
                xpath_os_version = f'//*[@id="os-driver-list"]/div[4]/div/div/div[2]//a[@keycode={os_version_keycode}]'

                WebDriverWait(web_engine, timeout=10).until(
                    lambda d: d.find_element(By.XPATH, xpath_os_version)
                )
                presence_of_element_located(xpath_os_version)
                section_selected_os_version = web_engine.find_element(By.XPATH, xpath_os_version)
                section_selected_os_version.click
                self.output(f"Selected the section for OS Version:  {os_version}", verbose_level=3)
            except:
                raise ProcessorError("Failed to select the desired OS Version")

            try:
                # Get the hyperlink for the driver download file
                download_url = section_selected_os_version.find_element(By.XPATH, 
                    '//*[@id="os-driver-list"]/div[4]/div/div/div[2]/div[1]/div/div/div[2]/div/div/div/div/div/div[1]/p[2]/a').get_attribute("href"
                )
            except:
                raise ProcessorError(
                    "Failed to find and collect the download url from the download button.")

        if not download_url:
            raise ProcessorError("Failed to find a matching download type for the provided model.")

        self.env["url"] = download_url
        self.output(f'Download URL: {self.env["url"]}', verbose_level=1)


if __name__ == "__main__":
    PROCESSOR = RicohPrintDriverURLProvider()
    PROCESSOR.execute_shell()
