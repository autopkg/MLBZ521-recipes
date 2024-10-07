#!/usr/local/autopkg/python
#
# Copyright 2024 Zack Thompson (MLBZ521)
# Thanks to knowledge shared by Richard Purves:
#   https://richard-purves.com/2022/05/15/downloading-beyondtrust-remote-support-via-api-for-fun-and-profit/
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

import base64
import json

import requests

from autopkglib import ProcessorError, URLGetter


__all__ = ["BeyondTrustURLProvider"]


class BeyondTrustURLProvider(URLGetter):

    """
    This processor get the download URL for a BeyondTrust Remote Support client installer.
    (Formally known as Bomgar.)
    """

    description = __doc__
    input_variables = {
        "beyond_trust_client_id": {
            "required": True,
            "description": "CrowdStrike API Client ID."
        },
        "beyond_trust_client_secret": {
            "required": True,
            "description": "CrowdStrike API Client Secret."
        },
        "jump_group": {
            "required": True,
            "description": (
                "The Jump Group the Jump Client is associated with.  If a string is provided, it's "
                "assumed it's the Jump Group 'name,' however, if a integer is provided, it's "
                "assumed it's the Jump Group ID."
            )
        },
        "jump_client_config": {
            "required": False,
            "description": "The configuration used for the Jump Client Key."
        },
        "jump_client_platform": {
            "required": False,
            "default": "mac-dmg",
            "description": (
                "The platform to download a compatible Jump Client.  Default:  'mac-dmg'"
            ),
        },
        "beyond_trust_url": {
            "required": True,
            "description": "URL for your Beyond Trust instance."
        }
    }
    output_variables = {
        "download_url": {"description": "Returns the url to download."},
        "key_info": {
            "description": "Returns the Jump Client Key to be used with the Jump Client Installer."
        },
        "access_token": {
            "description": (
                "Bearer Token required to interact with the BeyondTrust Remote Support API."
            )
        }
    }


    def main(self):

        # Define variables
        beyond_trust_url = self.env.get("beyond_trust_url")
        client_id = self.env.get("beyond_trust_client_id")
        client_secret = self.env.get("beyond_trust_client_secret")
        jump_group = self.env.get("jump_group")
        jump_client_config = self.env.get("jump_client_config")
        dl_platform = self.env.get("jump_client_platform", "mac-dmg")

        # API Endpoints
        token_url = f"https://{beyond_trust_url}/oauth2/token"
        url_api_base = f"https://{beyond_trust_url}/api/config/v1"
        url_jump_group = f"{url_api_base}/jump-group"
        url_installer = f"{url_api_base}/jump-client/installer"

        # Verify the input variables were provided
        if not beyond_trust_url or beyond_trust_url == "%BEYOND_TRUST_URL%":
            raise ProcessorError("The input variable 'BEYOND_TRUST_URL' was not set!")
        if not client_id or client_id == "%BEYOND_TRUST_CLIENT_ID%":
            raise ProcessorError("The input variable 'BEYOND_TRUST_CLIENT_ID' was not set!")
        if not client_secret or client_secret == "%BEYOND_TRUST_CLIENT_SECRET%":
            raise ProcessorError("The input variable 'BEYOND_TRUST_CLIENT_SECRET' was not set!")
        if not jump_group or jump_group == "%JUMP_GROUP%":
            raise ProcessorError("The input variable 'JUMP_GROUP' was not set!")

        # Base64 encode the OAuth Credentials
        base_encoded_creds = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

        # Get a Bearer Token
        request_token = requests.post(
            url = token_url,
            headers = {
                "accept": "application/json",
                "Authorization": f"Basic {base_encoded_creds}"
            },
            data = {"grant_type": "client_credentials"}
        )

        if request_token.status_code != 200:
            raise ProcessorError("Failed to obtain a bearer token from the API!")

        # Extract the Bearer "Access" Token
        access_token = request_token.json().get("access_token")
        self.output(f"API Access Token:  {access_token}", verbose_level=3)

        # Check if the provide value is an integer or string
        try:
            if isinstance(int(jump_group), int):
                jump_group_id = jump_group
        except ValueError:
            # If the Jump Group Name was provided, get it's ID
            # Get the list of Jump Groups
            request_jump_groups = requests.get(
                url = f"{url_jump_group}",
                headers = {
                    "accept": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
            )

            if request_jump_groups.status_code != 200:
                raise ProcessorError("API lookup for the Jump Group ID failed!")

            # Find the Jump Group and get it's ID
            for jump_group_object in request_jump_groups.json():
                if jump_group_object.get("name") == jump_group:
                    jump_group_id = jump_group_object.get("id")
                    break

            self.output(f"Jump Group ID:  {jump_group_id}", verbose_level=3)

        jump_client_config = json.loads(jump_client_config)
        jump_client_config |= {
            "jump_group_id": jump_group_id
        }

        # Create an Jump Client Key and Installer ID which is used to download a client installer.
        request_installer_id = requests.post(
            url = f"{url_installer}",
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            data = json.dumps(jump_client_config)
        )

        if request_installer_id.status_code != 200:
            raise ProcessorError("Failed to generate a Jump Client Key and Installer ID!")

        # Extract the bits
        installer_id = request_installer_id.json().get("installer_id")
        key_info = request_installer_id.json().get("key_info")
        download_url = f"{url_installer}/{installer_id}/{dl_platform}"

        self.env["download_url"] = download_url
        self.output(f"Download URL:  {download_url}", verbose_level=1)
        self.env["key_info"] = key_info
        self.output(f"Jump Client Key Info:  {key_info}", verbose_level=1)
        self.env["access_token"] = access_token
        self.output(f"API Access Token:  {access_token}", verbose_level=3)


if __name__ == "__main__":
    processor = BeyondTrustURLProvider()
    processor.execute_shell()
