#!/usr/bin/env python
#
# Copyright 2020 Zack Thompson (mlbz521)
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

from autopkglib import Processor, ProcessorError, URLGetter

__all__ = ["CrowdStrikeProcessor"]

class CrowdStrikeProcessor(URLGetter):

    """This processor finds the download URL for the CrowdStrike Sensor 
    version of the supplied Policy ID."""

    input_variables = {
        "client_id": {
            "required": True,
            "description": "CrowdStrike API Client ID."
        },
        "client_secret": {
            "required": True,
            "description": "CrowdStrike API Client Secret."
        },
        "policy_id": {
            "required": True,
            "description": "CrowdStrike Policy ID to get the assigned Sensor version."
        }
    }
    output_variables = {
        "download_url": {
            "description": "Returns the url to download."
        },
        "version": {
            "description": "Returns the version of the package to download."
        },
        "access_token": {
            "description": "Authorization Bearer Token required to interact with the CrowdStrike API."
        }
    }

    description = __doc__

    def main(self):

        # Define variables
        client_id = self.env.get('client_id')
        client_secret = self.env.get('client_secret')
        policy_id = self.env.get('policy_id')
        token_url = "https://api.us-2.crowdstrike.com/oauth2/token"
        policy_url = "https://api.us-2.crowdstrike.com/policy/combined/sensor-update/v1?filter=platform_name%3A'Mac'"
        installer_url = "https://api.us-2.crowdstrike.com/sensors/combined/installers/v1?filter=platform%3A%22mac%22"

        # Verify the input variables were provided
        if not client_id or client_id == "%CLIENT_ID%":
            raise ProcessorError("The input variable 'client_id' was not set!")
        if not client_secret or client_secret == "%CLIENT_SECRET%":
            raise ProcessorError("The input variable 'client_secret' was not set!")
        if not policy_id or policy_id == "%POLICY_ID%":
            raise ProcessorError("The input variable 'policy_id' was not set!")

        # Build the headers
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Build the required curl switches
        curl_opts = [
            "--url", "{}".format(token_url),
            "--request", "POST",
            "--data", "client_id={client_id}&client_secret={client_secret}".format(client_id=client_id, client_secret=client_secret)
        ]

        try:
            # Initialize the curl_cmd, add the curl options, and execute the curl
            curl_cmd = self.prepare_curl_cmd()
            self.add_curl_headers(curl_cmd, headers)
            curl_cmd.extend(curl_opts)
            response_token = self.download_with_curl(curl_cmd)

        except:
            raise ProcessorError("Failed to acquire bearer authentication token!")

        try:
            # Load the JSON Response
            json_data = json.loads(response_token)
            access_token = json_data["access_token"]
            # self.output(access_token)

            auth_headers = {
                "accept": "application/json",
                "authorization": "bearer {}".format(access_token)
            }

            # Execute curl
            response_policies = self.download(url=policy_url, headers=auth_headers)

        except:
            raise ProcessorError("Failed to get the Sensor Update Policies!")

        try:
            # Load the JSON Response
            json_data = json.loads(response_policies)

            # Loop through the Policies to find the desired Policy ID
            for policy in json_data["resources"]:

                if policy.get("id") == policy_id:

                    # Get the build assigned to the Policy
                    build = policy.get("settings")["build"]

            build_version = build.split('|', 1)[0]
            self.output("build_version:  {}".format(build_version))

        except:
            raise ProcessorError("Failed to match a Sensor Update Policy!")

        try:
            # Execute curl
            response_installers = self.download(url=installer_url, headers=auth_headers)

            # Load the JSON Response
            json_data = json.loads(response_installers)

            # Loop through the installers to to find the desired build
            for installer in json_data["resources"]:

                # The build is the last string of digits of the version string
                if installer.get("version").split('.')[-1] == build_version:
                    version = installer.get("version")
                    sha256 = installer.get("sha256")

        except:
            raise ProcessorError("Failed to acquire list of installers!")

        try:
            download_url = "https://api.us-2.crowdstrike.com/sensors/entities/download-installer/v1?id={}".format(sha256)
            self.output("download_url:  {}".format(download_url))

            # Return results
            self.env["access_token"] = access_token
            self.output("access_token: {}".format(self.env["access_token"]))
            self.env["version"] = version + ".0" # This is appended to match the _actual_ CFBundleShortVersionString
            self.output("version: {}".format(self.env["version"]))
            self.env["download_url"] = download_url
            self.output("download_url: {}".format(self.env["download_url"]))

        except:
            raise ProcessorError("Unable to find an installer that is assigned to the requested policy!")

if __name__ == "__main__":
    processor = CrowdStrikeProcessor()
    processor.execute_shell()
