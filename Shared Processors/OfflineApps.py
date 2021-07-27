#!/usr/bin/python
#
# Copyright 2020 Zack Thompson (MLBZ521)
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
'''See docstring for OfflineApps class'''

from __future__ import absolute_import
import os
import shutil
from pkg_resources import parse_version as Compare_Version
from autopkglib import Processor, ProcessorError

__all__ = ["OfflineApps"]

class OfflineApps(Processor):
    '''Used to locate and "download" offline application content that can 
    then be used for child pkg recipes.  This is for applications that are 
    behind a login or not available via normal internet "acquisitional" 
    methods.
    '''

    input_variables = {
        'search_path': {
            'description': 'Root path to search within.',
            'required': True,
        },
        'search_string': {
            'description': ('String that will be used to match items in the '
                            'search_path.'),
            'required': True,
        },
        'major_version': {
            'description': ('The major version that will be used to match '
                            'items in the search_path.'),
            'required': False,
        },
        'exception_string': {
            'description': ('String will exclude items from matching the '
                            'search'),
            'required': False,
        },
        'limitation_string': {
            'description': ('String that will further limit matching the '
                            'search'),
            'required': False,
        },
        'version_separator': {
            'description': ('Character used to separate the '
                            '"Software Title Name" from the "Version".'
                            'For example:  CrowdStrike Falcon-5.27.10803.0'
                            'The hyphen would be the separator character.'
                            'Defaults to "-"'),
            'default': '-',
            'required': False,
        },
        'max_depth': {
            'description': ('Maximum depth of folders to iterate through.'),
            'default': '1',
            'required': False,
        }
    }
    output_variables = {
        'version': {
            'description': ('The highest version found according to '
                            'pkg_resources.parse_version logic.')
        },
        'found_major_version': {
            'description': ('The highest version found according to '
                            'pkg_resources.parse_version logic.')
        },
        'cached_path': {
            'description': ('Path to the existing contents in the AutoPkg '
                            'Cache.')
        }
    }

    description = __doc__

    def walk(self, top, maxdepth):
        '''Returns a list of files and folders given a root path to transverse.'''
        dirs, nondirs = [], []

        for name in os.listdir(top):
            (dirs if os.path.isdir(os.path.join(top, name)) else nondirs).append(name)

        yield top, dirs, nondirs

        if maxdepth > 1:
            for name in dirs:
                for x in self.walk(os.path.join(top, name), maxdepth-1):
                    yield x

    def get_latest_version(self, found_items, major_version_like, version_separator):
        '''Determines the highest version number of the provided strings.'''
        latest_version = None
        latest_version_folder = None
        # print('found_items:  {}'.format(found_items))

        # Loop through the found items
        for item in found_items:
            # print('item:  {}'.format(item))
            item_version = item.split(version_separator)[-1]
            # print('item_version:  {}'.format(item_version))
            # print('latest_version:  {}'.format(latest_version))

            # If a major_version is supplied to reference, make sure the version string starts with supplied major version
            if major_version_like and not item_version.startswith(major_version_like):
                self.output("Does not match major_version")
                continue

            if Compare_Version(item_version) > Compare_Version(latest_version):
                # print("Matches major_version")
                latest_version = item_version
                latest_version_folder = item

        self.output("Newest version found:  {}".format(latest_version))
        return latest_version, latest_version_folder

    def main(self):

        # Get environment variables
        search_path = self.env.get('search_path')
        foldername_contains = self.env.get('search_string')
        foldername_not_contain = self.env.get('exception_string')
        foldername_must_contain = self.env.get('limitation_string')
        major_version_like = self.env.get('major_version')
        version_separator = self.env.get('version_separator')
        max_depth = self.env.get('max_depth')
        RECIPE_CACHE_DIR = self.env.get('RECIPE_CACHE_DIR')

        # Define local variables
        downloads_dir = os.path.join(RECIPE_CACHE_DIR, 'downloads')
        search_string = '{0}'
        directory_list = list()
        folder_list = list()

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

                # If the foldername contains a string it should not contain, skip it
                if foldername_not_contain and (foldername_not_contain in foldername):
                    continue

                # If the foldername does not contain a secondary string it should contain, skip it
                if foldername_must_contain and (foldername_must_contain not in foldername):
                    continue

                # Append matching folder to list for future use
                folder_list.append(os.path.join(root_directory, foldername))
                self.output("Matched:  {}".format(foldername))

        if len(folder_list) == 0:
                raise ProcessorError("Was not able to find a match!")

        else:
            # Get the latest version from the matched results
            self.env['version'], version_location = self.get_latest_version(folder_list, major_version_like, version_separator)

            # if self.env['version'] and version_location not None:
            if None in { self.env['version'], version_location }:
                raise ProcessorError("Was not able to match a version!")

            else:
                self.output('Latest version:  {}'.format(self.env['version']))
                self.env['found_major_version'] = (self.env['version']).split(".", 1)[0]
                self.output('Found major version:  {}'.format(self.env['found_major_version']))
                self.output('Location:  {}'.format(version_location))
                version_folder = (version_location).split("/")[-1]

                # Set the location where version should be cached
                self.env['cached_path'] = os.path.join(downloads_dir, version_folder)

                # Check if this has already been cached
                if os.path.exists(self.env['cached_path']):
                    self.output('Latest version already downloaded to the AutoPkg Cache:  {}'.format(self.env['cached_path']))
                else:
                    self.output('Downloading:  {}'.format(version_folder))
                    shutil.copytree(version_location, self.env['cached_path'])

if __name__ == '__main__':
    PROCESSOR = OfflineApps()
    PROCESSOR.execute_shell()
