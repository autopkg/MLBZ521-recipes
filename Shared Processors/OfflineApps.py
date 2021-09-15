#!/usr/bin/python
#
# Copyright 2021 Zack Thompson (MLBZ521)
#
# Based on work by:
#   Jesse Peterson / https://github.com/facebook/Recipes-for-AutoPkg/blob/master/Shared_Processors/SubDirectoryList.py
#       SubDirectoryList
#   Graham R Pugh / https://github.com/autopkg/grahampugh-recipes/tree/master/CommonProcessors
#       SubDirectoryList
#       LocalRepoUpdateChecker
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
"""See docstring for OfflineApps class"""

from __future__ import absolute_import

import os
import sys

from pkg_resources import parse_version

sys.path.insert(0, "/Library/AutoPkg/JSSImporter")
import jss

from autopkglib import Processor, ProcessorError, URLDownloader


__all__ = ["OfflineApps"]


class OfflineApps(URLDownloader):
    """Used to locate and "download" offline application content that can 
    then be used for child pkg recipes.  This is for applications that are 
    behind a login or not available via normal internet "acquisitional" 
    methods.
    """

    input_variables = {
        "search_path": {
            "description": "Root path to search within.",
            "required": True
        },
        "OFFLINEAPPS_SMB_URL": {
            "description": (
                "An optional SMB URL to mount containing the search path."
            ),
            "required": False
        },
        "OFFLINEAPPS_SMB_SHARE_NAME": {
            "description": "Share to mount from the SMB server.",
            "required": False
        },
        "OFFLINEAPPS_SMB_PORT": {
            "description": (
                "Port to use to connect to the SMB server.  "
                "Default port used is 445."
            ),
            "default": "445",
            "required": False
        },
        "OFFLINEAPPS_SMB_MOUNT_POINT": {
            "description": (
                "Where the SMB share will be mounted too.  "
                "Default mount point will be '/tmp/OfflineApps/'."
            ),
            "default": "/tmp/OfflineApps/",
            "required": False
        },
        "OFFLINEAPPS_SMB_USERNAME": {
            "description": "Username required to connect to the SMB server.",
            "required": False
        },
        "OFFLINEAPPS_SMB_PASSWORD": {
            "description": "Password required to connect to the SMB server.",
            "required": False
        },
        "OFFLINEAPPS_SMB_DOMAIN": {
            "description": "Domain, if required, to connect to the SMB server.",
            "required": False
        },
        "search_string": {
            "description": (
                "String that will be used to match items in the search_path."
            ),
            "required": True,
        },
        "major_version": {
            "description": (
                "The major version that will be used to match "
                "items in the search_path."
            ),
            "required": False,
        },
        "exception_string": {
            "description": "String will exclude items from matching the search",
            "required": False,
        },
        "limitation_string": {
            "description": "String that will further limit matching the search",
            "required": False,
        },
        "version_separator": {
            "description": (
                "Character used to separate the "
                "\"Software Title Name\" from the \"Version\"."
                "For example:  CrowdStrike Falcon-5.27.10803.0"
                "The hyphen would be the separator character."
                "Defaults to \"-\""
            ),
            "default": "-",
            "required": False,
        },
        "max_depth": {
            "description": "Maximum depth of folders to iterate through.",
            "default": "1",
            "required": False,
        },
        "check_filesize": {
            "default": True,
            "required": False,
            "description": (
                "If True, each file size will be checked to verify whether "
                "a download is newer than a cached item. This "
                "is useful to prevent re-downloading files that already exist."
                "Defaults to True."
            ),
        }
    }
    output_variables = {
        "version": {
            "description": (
                "The highest version found according to "
                "pkg_resources.parse_version logic."
            )
        },
        "found_major_version": {
            "description": "The \"major version\" of the version string found."
        },
        "cached_path": {
            "description": "Path to the existing contents in the AutoPkg Cache."
        },
        "download_changed": {
            "description": (
                "Boolean indicating if the download has changed since the "
                "last time it was downloaded."
            )
        }
    }

    description = __doc__


    def mount_via_jssimporter(self):
        """Mount a share via JSSImporter"""

        try:
            self.dp_instance = jss.distribution_point.SMBDistributionPoint(
                url = self.env.get("OFFLINEAPPS_SMB_URL"), 
                share_name = self.env.get("OFFLINEAPPS_SMB_SHARE_NAME"), 
                port = self.env.get("OFFLINEAPPS_SMB_PORT", "445"), 
                mount_point = self.env.get("OFFLINEAPPS_SMB_MOUNT_POINT", "/tmp/OfflineApps/"), 
                username = self.env.get("OFFLINEAPPS_SMB_USERNAME"), 
                password = self.env.get("OFFLINEAPPS_SMB_PASSWORD"), 
                domain = self.env.get("OFFLINEAPPS_SMB_DOMAIN"), 
                jss = jss.JSS(url="/")
            )

            self.dp_instance.mount()

        except:
            raise ProcessorError("Unable to mount the SMB share!")


    def walk(self, top, maxdepth):
        """Returns a list of files and folders given a root path to transverse."""
        dirs, nondirs = [], []

        for name in os.listdir(top):
            (dirs if os.path.isdir(os.path.join(top, name)) else nondirs).append(name)

        yield top, dirs, nondirs

        if maxdepth > 1:
            for name in dirs:
                yield from self.walk(os.path.join(top, name), maxdepth-1)


    def get_latest_version(self, found_items, major_version_like, version_separator):
        """Determines the highest version number of the provided strings."""
        latest_version = ""
        latest_version_folder = ""

        # Loop through the found items
        for item in found_items:
            item_version = item.split(version_separator)[-1]

            # If a major_version is supplied to reference, make sure 
            # the version string starts with supplied major version
            if major_version_like and not item_version.startswith(major_version_like):
                self.output("Does not match major_version", verbose_level=2)
                continue

            if parse_version(item_version) > parse_version(latest_version):
                latest_version = item_version
                latest_version_folder = item

        return latest_version, latest_version_folder


    def main(self):

        # Get environment variables
        search_path = self.env.get("search_path")
        smb_path = self.env.get("smb_path")
        foldername_contains = self.env.get("search_string")
        foldername_not_contain = self.env.get("exception_string")
        foldername_must_contain = self.env.get("limitation_string")
        major_version_like = self.env.get("major_version")
        version_separator = self.env.get("version_separator")
        max_depth = self.env.get("max_depth")
        check_filesize = self.env.get("check_filesize", True)
        RECIPE_CACHE_DIR = self.env.get("RECIPE_CACHE_DIR")
        self.env["download_changed"] = False

        # Define local variables
        downloads_dir = os.path.join(RECIPE_CACHE_DIR, "downloads")
        folder_list = []

        # Mount SMB share if passed
        if self.env.get("OFFLINEAPPS_SMB_URL"):
            self.mount_via_jssimporter()

        try:

            # Verify the directory exists
            if not os.path.isdir(search_path):
                raise ProcessorError("Can't find root path or network share not mounted!")

            # Build the directory list of the root of the search_path
            for root_directory, folders, files in self.walk(search_path, int(max_depth)):

                # Loop through the folders
                for foldername in folders:

                    # If the foldername does not contain a string it should contain, skip it
                    if foldername_contains and (foldername_contains not in foldername):
                        continue

                    # If the foldername contains the string it should not contain, skip it
                    if foldername_not_contain and (foldername_not_contain in foldername):
                        continue

                    # If the foldername does not contain the secondary 
                    # string it should contain, skip it
                    if foldername_must_contain and (foldername_must_contain not in foldername):
                        continue

                    # Append matching folder to list for future use
                    folder_list.append(os.path.join(root_directory, foldername))
                    self.output("Matched:  {}".format(foldername), verbose_level=2)

            if not folder_list:
                raise ProcessorError("Was not able to find a match!")

            # Get the latest version from the matched results
            self.env["version"], version_location = self.get_latest_version(
                folder_list, major_version_like, version_separator)

            if None in { self.env["version"], version_location }:
                raise ProcessorError("Was not able to match a version!")

            self.env["found_major_version"] = (self.env["version"]).split(".", 1)[0]
            version_folder = (version_location).split("/")[-1]

            self.output("Found major version:  {}".format(
                self.env["found_major_version"]), verbose_level=2)
            self.output("Latest version found:  {}".format(self.env["version"]))
            self.output("Location:  {}".format(version_location), verbose_level=2)

            # Set the location where version should be cached
            self.env["cached_path"] = os.path.join(downloads_dir, version_folder)

            # Loop over files in version_location and download each one?
            for root_directory, folders, files in self.walk(version_location, int(0)):

                for file in files:

                    server_path = "{}/{}".format(version_location, file)
                    save_path = "{}/{}".format(self.env["cached_path"], file)

                    if os.path.exists(save_path) and check_filesize and \
                        os.path.getsize(server_path) == os.path.getsize(save_path):
                        self.output("File exists locally, not downloading...")
                        continue

                    self.output("Downloading file:  {}".format(file))
                    self.output("Path where file will be saved:  {}".format(
                        save_path), verbose_level=2)

                    # Build the required curl switches
                    curl_opts = [
                        "--url", "file://{}".format(server_path),
                        "--request", "GET",
                        "--output", save_path,
                        "--create-dirs"
                    ]

                    try:
                        # Initialize the curl_cmd, add the curl options, and execute the curl
                        curl_cmd = self.prepare_curl_cmd()
                        curl_cmd.extend(curl_opts)
                        self.download_with_curl(curl_cmd)
                        self.env["download_changed"] = True

                    except:
                        raise ProcessorError("Failed to download:  {}".format(file))

        finally:

            # Done with distribution point, unmount it.
            if self.env.get("OFFLINEAPPS_SMB_URL") and self.dp_instance.is_mounted():
                self.dp_instance.umount()


if __name__ == "__main__":
    PROCESSOR = OfflineApps()
    PROCESSOR.execute_shell()
