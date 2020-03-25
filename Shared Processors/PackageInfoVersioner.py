#!/usr/bin/python

# Copyright 2020 dataJAR
# https://github.com/autopkg/dataJAR-recipes/blob/master/Shared%20Processors/DistributionPkgInfo.py
#
# Modified by Zack Thompson
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

# pylint: disable=import-error, too-few-public-methods

"""See docstring for PackageInfoVersioner class"""

from __future__ import absolute_import

import os.path
from xml.etree import ElementTree

from autopkglib import Processor, ProcessorError

__all__ = ["PackageInfoVersioner"]
__version__ = '1.0'

class PackageInfoVersioner(Processor):
    """Parses a distribution pkg to pull the info, 
    other formats to be added later"""

    description = __doc__
    input_variables = {
        "path": {
            "required": True,
            "description": ("Path to the .pkg.")
        }
    }

    output_variables = {
        "version": {
            "description": ("The version of the pkg from it's info")
        },
        "bundleid": {
            "description": ("The bundle id of the pkg from it's info")
        }
    }

    # pylint: disable=too-many-branches
    def main(self):
        """Cobbled together from various sources, should extract information 
        from a Distribution pkg"""
        # Build dir as needed,pinched with <3 from:
        # https://github.com/autopkg/autopkg/blob/master/Code/autopkglib/FlatPkgUnpacker.py#L72
        # Extract pkg info, pinched with <3 from:
        # https://github.com/munki/munki/blob/master/code/client/munkilib/pkgutils.py#L374

        path = os.path.join(self.env["path"])
        pkg_info_path = os.path.join(path, "PackageInfo")
        version = None

        if not os.path.exists(pkg_info_path):
            raise ProcessorError("Cannot find PackageInfo")
        else:
            tree = ElementTree.parse(pkg_info_path)

            try:
                bundle_info = tree.findall('//bundle-version/bundle')[0]
                version = bundle_info.get('CFBundleShortVersionString')
                bundleid = bundle_info.get('id')

            except ElementTree.ParseError as err:
                print("Can't parse PackageInfo file {}: {}".format(pkg_info_path, err.strerror))

        if not version:
            raise ProcessorError("Cannot get version")
        else:
            self.env["version"] = version
            self.env["bundleid"] = bundleid

if __name__ == '__main__':
    PROCESSOR = PackageInfoVersioner()
