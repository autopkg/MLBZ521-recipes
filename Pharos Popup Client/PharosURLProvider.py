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

import glob
import os
import re
import sys
import tempfile
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
        "pathname": {"description": "Path to the downloaded file."},
        "download_changed": {
            "description": (
                "Boolean indicating if the download has changed since the "
                "last time it was downloaded."
            )
        },
        "url_downloader_summary_result": {
            "description": "Description of interesting results."
        },
    }

    description = __doc__


    def make_tmp_dir(self, tmp_dir):
        """make the tmp directory"""
        return tempfile.mkdtemp(prefix="tmp_", dir=tmp_dir)


    def main(self):
        """Do the main thing."""

        # Define variables
        downloads_page = self.env.get("downloads_page",
            "https://community.pharos.com/s/article/Macintosh-Updates-For-Uniprint")
        prefix_dl_url = self.env.get("prefix_dl_url",
            "https://private.filesanywhere.com/PHAROS/")
        prefix_dl_url = re.sub(r"\s", "%20", prefix_dl_url)
        web_driver = self.env.get("web_driver", "Chrome")
        web_driver_path = self.env.get("web_driver_path")
        web_driver_binary_location = self.env.get("web_driver_binary_location")
        web_engine_headless = bool(self.env.get("WEB_ENGINE_HEADLESS"))


        RECIPE_DL_DIR = f"{self.env.get('RECIPE_CACHE_DIR')}/downloads"
        if not os.path.exists(RECIPE_DL_DIR):
            os.mkdir(path=RECIPE_DL_DIR)
        tmp_dl_dir = self.make_tmp_dir(RECIPE_DL_DIR)
        self.env["tmp_dl_dir"] = tmp_dl_dir

        get_download_links = None

        with WebEngine(engine=web_driver, binary=web_driver_binary_location, path=web_driver_path,
            headless=web_engine_headless, parent=self) as web_engine:

            try:
                web_engine.get(downloads_page)
                get_download_links = WebDriverWait(web_engine, timeout=10).until(
                    lambda d: d.find_elements(By.LINK_TEXT, "Download")
                )
            except:
                raise ProcessorError("Failed to access the download page.")

            if not get_download_links:
                raise ProcessorError(
                    f"Unable to find link to the download page:  {self.env.get('downloads_page')}")

            try:
                for link in get_download_links:
                    self.output(f"Found possible download page:  {link.get_attribute('href')}", verbose_level=3)

                    if re.match(prefix_dl_url, link.get_attribute("href")):
                        download_host = link.get_attribute("href")
                        self.output("  * Matching Link", verbose_level=3)
                        break
            except:
                raise ProcessorError(
                    "Failed to find and collect the download url from the download link.")

            if not download_host:
                raise ProcessorError(
                    f"Unable to find matching download link on:  {self.env.get('downloads_page')}")

            try:
                web_engine.get(download_host)
                email_box = WebDriverWait(web_engine, timeout=10).until(
                    lambda d: d.find_elements(By.NAME, "verificationText")
                )
                # Enter an email address
                email_box[0].click()
                email_box[0].send_keys("anon@anonymous.anon")
                # Click the I Agree button
                agree_checkbox = web_engine.find_elements(By.NAME, "checkboxApproval")
                agree_checkbox[0].click()
                # Click the Continue button
                continue_button = web_engine.find_elements(By.ID, "btnContinue")
                continue_button[0].click()

            except:
                raise ProcessorError(
                    "Something went wrong attempting to fill out the 'Export Administration Regulations' form.")

            try:

                folder_links = WebDriverWait(web_engine, timeout=10).until(
                    lambda d: d.find_elements(By.XPATH, "//*[contains(@title, 'Mac OS X Popups')]")
                )

                for folder_link in folder_links:
                    self.output(f"Found folder the title:  {folder_link.get_attribute('title')}", verbose_level=3)

                    if re.match("Mac OS X Popups", folder_link.get_attribute("title")):
                        self.output("  * Guessing this is the link...", verbose_level=3)
                        break

                folder_link.click()
                time.sleep(1)

            except:
                raise ProcessorError(
                    "Something went wrong attempting to find the folder link.")

            try:
                download_links = WebDriverWait(web_engine, timeout=10).until(
                    lambda d: d.find_elements(By.XPATH, "//*[contains(@onclick, 'Mac OS X Popups')]")
                )

                for download_link in download_links:
                    self.output(f"Found a download link:  {download_link.get_attribute('onclick')}", verbose_level=3)

                    if re.match(r".*Mac OS X Popups.*", download_link.get_attribute("onclick")):
                        self.output("  * Guessing this is the link...", verbose_level=3)
                        break

                download_link.click()

            except:
                raise ProcessorError(
                    "Something went wrong attempting to find the download link.")

        # Hack to monitor for download start and completion
        # Wait for a temporary download file to exist and then no longer exist
        self.output("Waiting for download to start...")
        started = lambda x: len(x(f"{tmp_dl_dir}/*.crdownload")) > 0
        WebDriverWait(glob.glob, 300).until(started)
        self.output("Download has started...")

        completed = lambda x: len(x(f"{tmp_dl_dir}/*.crdownload")) == 0
        WebDriverWait(glob.glob, 300).until(completed)
        self.output("Download has completed!")

        # Get the name of the download file
        file = os.listdir(path=tmp_dl_dir)[0]

        # Move the file to the standard download directory
        os.rename(src=f"{tmp_dl_dir}/{file}", dst=f"{RECIPE_DL_DIR}/{file}")

        # Delete the temporary download directory
        os.rmdir(path=tmp_dl_dir)

        self.env["pathname"] = f"{RECIPE_DL_DIR}/{file}"
        self.env["download_changed"] = True

        # Generate output messages and variables
        self.output(f"Downloaded {self.env['pathname']}")
        self.env["url_downloader_summary_result"] = {
            "summary_text": "The following new items were downloaded:",
            "data": {"download_path": self.env["pathname"]},
        }


if __name__ == "__main__":
    PROCESSOR = PharosURLProvider()
    PROCESSOR.execute_shell()
