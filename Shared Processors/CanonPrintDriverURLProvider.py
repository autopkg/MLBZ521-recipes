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
import os
import re
import sys
import time

from pkg_resources import parse_version

from autopkglib import ProcessorError, URLGetter

if not os.path.exists("/Library/AutoPkg/Selenium"):
    raise ProcessorError("Selenium is required for this recipe!  "
    "Please review my Shared Processors README.")

sys.path.insert(0, "/Library/AutoPkg/Selenium")
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import (
    element_to_be_clickable, presence_of_element_located, visibility_of_element_located)
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException

sys.path.insert(0,
    f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/Shared Processors")
from SeleniumWebScrapper import WebEngine


__all__ = ["CanonPrintDriverURLProvider"]


class CanonPrintDriverURLProvider(URLGetter):
    """This processor finds the download URL for the "recommended" Canon print driver.
    """

    description = __doc__
    input_variables = {
        "model": {
            "required": True,
            "description": (
                "The official model name of the Canon Printer to search for."
            )
        },
        "os_version": {
            "required": False,
            "description": (
                "The OS version to search against.",
                "Default:  'MACOS_14' (i.e. Sonoma)",
            ),
            "default": "MACOS_14"
        },
        "web_driver": {
            "required": False,
            "description": (
                "The web driver engine to use.  Only Chrome is supported at this time, "
                "but support for additional web drivers can be added.",
                "Default:  Chrome"
            ),
            "default": "Chrome"
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
                "The path to the browser's binary.  Defaults to using Google Chrome for Testing.",
                "Default:  /Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
            ),
            "default": "/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
        },
        "download_type": {
            "required": False,
            "description": (
                "What to download from the available list. For example:",
                "   - \"Recommended\" will download whatever option is in the "
                "       \"Recommended Driver(s)\" section.",
                "       Note:  The \"Recommended\" driver may not be the *_latest_* driver.",
                "   - \"UFRII\" will download the latest UFRII driver",
                "   - \"PS\" will download the latest PS driver",
                "   - \"FAX\" will download the latest FAX driver",
                "   - \"PPD\" will download the latest PPD driver",
                "   - \"MF\" will download the latest MF driver",
                "   - \"Scanner\" will download the latest Scanner driver",
                "Default:  Recommended"
            ),
            "default": "Recommended"
        }
    }
    output_variables = {
        "url": {
            "description": "Returns the url to download."
        }
    }


    def scroll_into_view_and_click(self, web_engine, xpath):
        """Scrolls the provided xpath element into view and clicks it.

        Args:
            web_engine (WebEngine): Instantiated WebEngine loaded to a url
            xpath (str): xpath formatted query
        """

        WebDriverWait(web_engine, 10).until(presence_of_element_located((By.XPATH, xpath)))
        WebDriverWait(web_engine, 10).until(visibility_of_element_located((By.XPATH, xpath)))
        WebDriverWait(web_engine, 10).until(element_to_be_clickable((By.XPATH, xpath)))
        element = web_engine.find_element(By.XPATH, xpath)
        web_engine.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(1)
        ActionChains(web_engine).move_to_element(element).click().perform()
        time.sleep(1)


    def main(self):
        """Do the main thing."""

        # Define variables
        model = self.env.get("model")
        os_version = self.env.get("os_version", "MACOS_14")
        web_driver = self.env.get("web_driver", "Chrome")
        web_driver_path = self.env.get("web_driver_path")
        web_driver_binary_location = self.env.get("web_driver_binary_location")
        download_type = self.env.get("download_type", "Recommended")

        self.output(f"Searching for printer model:  {model}", verbose_level=1)
        # Canon's json product list URL:  https://downloads.canon.com/c16415dev/cusa/ow/support/support-home-products.json
        # Used to use the above URL for looking up printer, leaving it documented here for future reference

        # Build the required curl switches
        curl_opts = [
            "--url", "https://platform.cloud.coveo.com/rest/search/v2?organizationId=canonusaproductionw69lguud",
            "--data-raw",
            '{{ "locale": "en-US", "debug": false, "tab": "default", "referrer": "default", "timezone": "America/Phoenix", "visitorId": "", "context": {{ "environment": "PROD", "contentType": "productSupport", "website": "CanonProductFinder" }}, "fieldsToInclude": [ "author", "language", "urihash", "objecttype", "collection", "source", "permanentid", "filetype", "commoncontenttype", "aem_contenttype", "aem_author", "aem_thumbnail", "aem_description", "aem_instructor", "aem_length", "aem_price", "article_type", "aem_skilllevel", "aem_type", "article_description", "commonsupportcontenttype", "aem_videourl", "ineturl", "size", "aem_startdate", "aem_enddate", "clickableuri", "aem_damsize", "aem_tc", "aem_contenttypevalue", "ec_thumbnails", "out_of_support_life", "bv_product_rating", "bv_avg_product_rating", "bv_number_of_reviews", "product_url", "spdp_url", "product_badges", "ec_store_id", "base_price", "final_price", "price", "bestsellers", "aem_sortdate", "sku", "thumbnail", "description", "color", "title", "product_id", "eight_digits_sku", "merchandise_type", "aem_advisories_flag", "aem_apps_flag", "aem_error_codes_flag", "aem_faqs_flag", "aem_fax_help_flag", "aem_how_to_videos_flag", "aem_manuals_flag", "aem_operating_system_compatibility_flag", "aem_service_upgrades_flag", "aem_technical_specifications_flag", "aem_warranty_info_flag", "aem_wireless_help_flag", "aem_software_drivers_flag", "aem_supplies_accessories_flag", "aem_software_development_kit_flag", "aem_out_of_support_life_flag", "inetdescription", "retired_product", "ec_category", "okb_categories_hierarchy", "aem_producttype" ], "pipeline": "Canon Product Finder", "q": "{}", "enableQuerySyntax": false, "searchHub": "CanonProductFinder", "enableDidYouMean": false, "numberOfResults": 1, "firstResult": 0}}'.format(model),
        ]
        headers = {
            "authority": "platform.cloud.coveo.com",
            "authorization": "Bearer xxd7e4a0fb-bf17-4db6-bf06-0411bb13f96e",
            "content-type": "application/json",
            "origin": "https://www.usa.canon.com",
            "referer": "https://www.usa.canon.com/",
            # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        }

        try:
            # Initialize the curl_cmd, add the curl options, and execute curl
            curl_cmd = self.prepare_curl_cmd()
            self.add_curl_headers(curl_cmd, headers)
            curl_cmd.extend(curl_opts)
            result = self.download_with_curl(curl_cmd)

        except:
            raise ProcessorError("Failed to query the Canon API.")

        try:
            # Load the JSON Response
            json_data = json.loads(result)

            for result in json_data.get("results"):
                if result.get("title") == model:
                    model_url = result.get("uri")

            self.output(f"Model downloads page:  {model_url}", verbose_level=2)

        except:
            raise ProcessorError("Failed to find a matching model!")

        with WebEngine(
            engine=web_driver, binary=web_driver_binary_location, path=web_driver_path, parent=self
        ) as web_engine:

            try:
                web_engine.get(model_url)
                # Workaround for when the page fails to load new content after interacting with it
                web_engine.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                web_engine.delete_all_cookies()

            except:
                raise ProcessorError("Failed to access the model page.")

            try:
                # Select Software & Drivers section
                self.output("Expanding the 'Software & Drivers' section...", verbose_level=3)
                self.scroll_into_view_and_click(
                    web_engine,
                    "//*/div[contains(@class, 'accordion-title')][contains(text(), 'Software & Drivers')]"
                )

            except:
                raise ProcessorError("Failed to find and open the 'Software & Drivers' section.")

            try:

                # Open the "OS type" dropdown menu
                web_engine.find_element(By.CSS_SELECTOR,
                    "div[class='software-downloads'] div[class='os-dropdown os-names ada-clickable'] button[class='dropdown-btn']").click()
                time.sleep(1)
                # Select the "OS type"
                self.output("Selecting the OS type:  Mac", verbose_level=3)
                web_engine.find_element(By.XPATH,
                    "//*/ul[contains(@class, 'dropdown os-names-dropdown')]/li[@class='os-type'][@filtervalue='Mac']").click()
                time.sleep(1)

                # Open the "OS version" dropdown menu
                os_version_dropdown = web_engine.find_element(By.CSS_SELECTOR,
                    "div[class='software-downloads'] div[class='os-dropdown os-versions ada-clickable'] button[class='dropdown-btn']")
                os_version_dropdown.click()
                time.sleep(1)

                # Select the "OS version"
                self.output(f"Selecting the OS version:  {os_version}", verbose_level=3)
                web_engine.find_element(By.XPATH,
                    f"//*/ul[contains(@class, 'dropdown os-versions-dropdown')]/li[@osfamily='Mac'][@filtervalue='{os_version}']/a[@class='os-version__name']").click()
                self.output("The OS Version was selected.", verbose_level=3)
                time.sleep(1)

            except:
                raise ProcessorError("Failed attempting to select the desired OS type or version")

            try:

                # Open the "Sort" dropdown menu
                web_engine.find_element(By.XPATH,
                    "//*/div[contains(@class, 'os-dropdown medium downloads_sort ada-clickable')]").click()
                time.sleep(1)

                if re.match(download_type, "Recommended", re.IGNORECASE):
                    self.output(f"Sorting by:  {download_type}", verbose_level=3)
                    # Sort by Recommended
                    web_engine.find_element(By.XPATH,
                        f"//*/ul[@class='dropdown'][@filtertype='sort']/li[@filtervalue='{download_type}']").click()

                else:
                    # Sort by Date
                    self.output("Sorting by:  Date", verbose_level=3)
                    web_engine.find_element(By.XPATH,
                        "//*/ul[@class='dropdown'][@filtertype='sort']/li[@filtervalue='Date']").click()

                time.sleep(1)

            except:
                raise ProcessorError("Failed to sort the list of options.")

            if re.match(download_type, "Recommended", re.IGNORECASE):
                try:
                    download_url = web_engine.find_element(By.XPATH,
                        "//*/div[@class='software-downloads__container']/div[@recommended='Y']//div[@class='download__cta']//a[@role='button']").get_attribute("href")
                except:
                    raise ProcessorError(
                        "Failed to identify the download url for the Recommended download.")

            else:

                try:

                    # Click the "Load More" button to display all options _if_ the button is
                    # visible...it may be there, but it may not be visible...
                    if load_more_section := web_engine.find_element(By.XPATH,
                        "//*[contains(@class, 'advisories-load-more-button-container')]"):

                        if load_more := web_engine.find_element(By.XPATH,
                            "//*/a[@role='button'][contains(@class, 'softwares-load-more')][@style='display: inline-block;']"):

                            # This attempts to scroll the button into the middle of the screen
                            web_engine.execute_script(
                                'arguments[0].scrollIntoView({"block": "center", "inline": "center"});',
                                load_more_section
                            )
                            time.sleep(1)
                            web_engine.execute_script(
                                'arguments[0].scrollIntoView({"block": "center", "inline": "center"});',
                                load_more
                            )
                            time.sleep(1)
                            load_more.click()
                            time.sleep(1)

                except NoSuchElementException:
                    self.output("'Load More' button is not visible", verbose_level=2)

                # Get the downloads container element
                download_list = web_engine.find_element(By.XPATH,
                    "//*/div[@class='software-downloads__container']")

                if download_type in [ "UFRII", "PS", "FAX", "PPD" ]:

                    try:
                        # Find all the DOWNLOAD button elements
                        links = download_list.find_elements(By.PARTIAL_LINK_TEXT, "DOWNLOAD")

                        # Collect all the download links that match the download type
                        download_version_urls = [
                            link.get_attribute("href")
                            for link in links
                            if re.match(
                                fr"^{download_type}.+",
                                os.path.basename(link.get_attribute("href")),
                                re.IGNORECASE
                            )
                        ]

                    except:
                        raise ProcessorError("Failed find matches for the selected download_type.")

                    try:
                        # Parse the links by versioning information, build a dictionary of the
                        # versions, and determine the latest
                        download_version_urls_dict = {
                            parse_version(os.path.basename(url)): url for url in download_version_urls}

                    except:
                        raise ProcessorError(
                            "Failed to identify the the latest version to download.")

                else:

                    if download_type == "MF":
                        link_text = "mac-mf-"
                    elif download_type == "Scanner":
                        link_text = "mac-scan-"

                    # Find all the link elements
                    links = download_list.find_elements(By.XPATH,
                        f"//*/a[contains(@class, 'file-name-link')][contains(text(), '{link_text}')]")

                    # Parse the links by versioning information, build a dictionary of the
                    # versions, and determine the latest
                    download_version_urls_dict = {
                        parse_version(link.text): link.get_attribute("href") for link in links }

        try:
            download_url = download_version_urls_dict.get(
                max(download_version_urls_dict.keys()))

            # Return results
            self.env["url"] = download_url
            self.output(f"Download URL: {self.env['url']}", verbose_level=1)

        except:
            raise ProcessorError("Failed to find a download url for the provided model.")


if __name__ == "__main__":
    PROCESSOR = CanonPrintDriverURLProvider()
    PROCESSOR.execute_shell()
