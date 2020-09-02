#!/usr/local/autopkg/python
#
# Copyright 2013 Greg Neagle
#
# Customized the DMG/Versioner Processors - MLBZ521 (Zack Thompson)
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
"""See docstring for CFBundleInfo class"""

import os.path
import plistlib

from autopkglib import ProcessorError
from autopkglib.DmgMounter import DmgMounter

__all__ = ["CFBundleInfo"]


class CFBundleInfo(DmgMounter):
    """Returns version information from a plist"""

    description = __doc__

    input_variables = {
        "input_plist_path": {
            "required": True,
            "description": (
                "File path to a plist. Can point to a path inside a .dmg "
                "which will be mounted."
            )
        }
    }
    output_variables = {
        "cfbundle_version": {
            "description": "Value of CFBundleVersion."
        },
        "cfbundle_shortversionstring": {
            "description": "Value of CFBundleShortVersionString."
        },
        "cfbundle_identifier": {
            "description": "Value of CFBundleIdentifier."
        },
        "version": {
            "description": "Returns the .app's version for use in parent recipes."
        }
    }

    def main(self):
        """Return a version for file at input_plist_path"""
        # Check if we're trying to read something inside a dmg.
        (dmg_path, dmg, dmg_source_path) = self.parsePathForDMG(
            self.env["input_plist_path"]
        )
        try:
            if dmg:
                # Mount dmg and copy path inside.
                mount_point = self.mount(dmg_path)
                input_plist_path = os.path.join(mount_point, dmg_source_path)
            else:
                # just use the given path
                input_plist_path = self.env["input_plist_path"]
            if not os.path.exists(input_plist_path):
                raise ProcessorError(
                    f"File '{input_plist_path}' does not exist or could not be read."
                )
            try:
                with open(input_plist_path, "rb") as f:
                    plist = plistlib.load(f)

                self.env["version"] = plist.get("CFBundleShortVersionString", "UNKNOWN_VERSION")
                self.env["cfbundle_shortversionstring"] = plist.get("CFBundleShortVersionString", "UNKNOWN_VERSION")
                self.env["cfbundle_version"] = plist.get("CFBundleVersion", "UNKNOWN_VERSION")
                self.env["cfbundlebundle_identifier"] = plist.get("CFBundleIdentifier", "UNKNOWN_BUNDLEID")
                self.output(
                    f"Found version {self.env['cfbundle_shortversionstring']} in file {input_plist_path}"
                    f"Found CFBundleShortVersionString {self.env['cfbundle_shortversionstring']} in file {input_plist_path}"
                    f"Found CFBundleVersion {self.env['cfbundle_version']} in file {input_plist_path}"
                    f"Found CFBundleIdentifier {self.env['cfbundlebundle_identifier']} in file {input_plist_path}"
                )
            except Exception as err:
                raise ProcessorError(err)

        finally:
            if dmg:
                self.unmount(dmg_path)


if __name__ == "__main__":
    PROCESSOR = CFBundleInfo()
    PROCESSOR.execute_shell()
