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

from autopkglib import Processor, ProcessorError

if not os.path.exists("/Library/AutoPkg/Selenium"):
    raise ProcessorError("Selenium is required for this recipe!  "
        "Please review my Shared Processors README.")

sys.path.insert(0, "/Library/AutoPkg/Selenium")

from selenium import webdriver


__all__ = ["SeleniumWebScrapper"]


class WebEngine(Processor):
    """Creates a Context Manager for Selenium to interact with a WebDriver Engine.
    Not intended for direct use."""

    description = __doc__
    input_variables = {
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


    def __init__(self, engine, binary, parent=None, path=None, headless=True):
        self.binary = binary
        self.engine = engine
        self.headless = self.str2bool(headless)
        self.path = path
        self.parent = parent


    def __enter__(self):
        """Creates a Web Engine instance to interact with."""

        self.parent.output(f"Using Web Driver:  {self.engine}", verbose_level=3)
        self.parent.output(f"Web Driver Binary Location:  {self.binary}", verbose_level=3)

        if self.path:
            self.parent.output(f"Path to Web Driver Engine:  {self.path}", verbose_level=3)
        else:
            self.parent.output("The Web Driver Engine is assumed to be in the $PATH.", verbose_level=3)

        try:

            if self.engine == "Chrome":
                options = webdriver.ChromeOptions()
                options.binary_location = self.binary
                options.add_argument("window-size=1920,1080")
                options.add_argument("start-maximized")
                options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")

                if self.headless:
                    options.add_argument("headless")

                if self.parent.env.get("tmp_dl_dir"):
                    options.add_experimental_option(
                        "prefs",
                        {
                            "download.default_directory": self.parent.env.get("tmp_dl_dir"),
                            "download.prompt_for_download": False
                        }
                    )

                if self.path:
                    self.web_engine = webdriver.Chrome(executable_path=self.path, options=options)

                else:
                    self.web_engine = webdriver.Chrome(options=options)

        except Exception as error:
            raise ProcessorError("Failed to load the specified WebDriver engine.") from error

        return self.web_engine


    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Closes the web engine instance."""
        self.web_engine.close


    def str2bool(self, value):
        return str(value).lower() in {"true", "t", "yes", "1"}


    def main(self):
        pass


if __name__ == "__main__":
    PROCESSOR = WebEngine()
    PROCESSOR.execute_shell()
