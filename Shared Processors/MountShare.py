#!/usr/local/autopkg/python
#
# Copyright 2022 Zack Thompson (MLBZ521)
#
# Based on code found in `python-jss`'s distribution_point.py:
#   By:  Shea Craig, Mosen, and other contributors
#   https://github.com/jssimporter/python-jss/blob/master/jss/distribution_point.py
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
import re
import subprocess

from urllib.parse import quote

from autopkglib import Processor, ProcessorError


__all__ = ["MountShare"]


class MountShare(Processor):
	"""Mounts a share from an external server.

	Not intended for direct use."""

	description = __doc__
	input_variables = {
		"url": {
			"description": (
				"An SMB URL to mount."
			),
			"required": True
		},
		"share_name": {
			"description": "Share to mount from the SMB server.",
			"required": True
		},
		"port": {
			"description": (
				"Port to use to connect to the SMB server.  "
				"Default port used is 445."
			),
			"default": "445",
			"required": False
		},
		"mount_point": {
			"description": (
				"Where the SMB share will be mounted too.  "
				"Default mount point will be '/private/tmp/OfflineApps'."
			),
			"default": "/private/tmp/OfflineApps",
			"required": False
		},
		"protocol": {
			"description": (
				"The protocol used to connect to the url."
				"The default and currently only supported protocol is 'smb'."
			),
			"default": "smb",
			"required": False
		},
		"username": {
			"description": "Username, if required, to connect to the SMB server.",
			"required": False
		},
		"password": {
			"description": "Password, if required, to connect to the SMB server.",
			"required": False
		},
		"domain": {
			"description": "Domain, if required, to connect to the SMB server.",
			"required": False
		},
	}
	output_variables = {}
	required_attrs = {
		"url",
		"share_name",
		"mount_point",
		"domain",
		"username",
		"password",
	}


	def __init__(self, **connection_args):
		"""Store SMB connection information.
		Args:
			connection (dict): Dictionary for storing connection arguments.
			connection_args: Dict with the following key/val pairs:
				url: URL to the mountpoint,including volume name e.g.:
					"my_repository.domain.org/jamf" (Do _not_ include
					protocol or auth info.)
				mount_point: Path to a valid mount point.
				share_name: The fileshare's name.
				domain: Specify the domain.
				username: Share R/W username.
				password: Share R/W password.
		"""

		self.env = connection_args.get("env")

		if self.required_attrs.issubset(set(connection_args.keys())):
			self.connection = connection_args
			self._build_url()
		else:
			missing_attrs = self.required_attrs.difference(set(connection_args.keys()))
			raise ProcessorError(f"Missing REQUIRED argument(s) {list(missing_attrs)}")

		self.fs_type = self.connection.get("protocol") or "smbfs"


	def __repr__(self):
		"""Return string representation of connection arguments."""
		output = [
			f"Share:  {self.connection['url']}",
			f"Type: {type(self)}", "Connection Information:"
		]
		output.extend("\t%s: %s" % (key, val) for key, val in self.connection.items())
		return "\n".join(output) + "\n"


	@property
	def _encoded_password(self):
		"""Returns the safely url-quoted password for this DP."""
		return quote(self.connection["password"], safe="~()*!.'$")


	def _build_url(self):
		"""Build the URL string to mount this file share."""
		if self.connection.get("username") and self.connection.get("password"):
			auth = f"{self.connection['username']}:{self._encoded_password}@"
			pwless = f"{self.connection['username']}@"
			if self.connection.get("domain"):
				auth = f"{self.connection['domain']};{auth}"
				pwless = f"{self.connection['domain']};{pwless}"
		else:
			auth = ""
			pwless = ""
		port = self.connection.get("port")
		port = f":{port}" if port else ""

		self.connection["mount_url"] = f"//{auth}{self.connection['url']}{port}/{self.connection['share_name']}"
		self.connection["mount_url_passwordless"] = f"//{pwless}{self.connection['url']}{port}/{self.connection['share_name']}"


	def mount(self):
		"""Mount the SMB Share"""

		# Ensure the mount point directory exists
		if not os.path.exists(self.connection["mount_point"]):
			os.mkdir(self.connection["mount_point"])

		self.output(f"Mount point will be:  {self.connection['mount_point']}", verbose_level=3)

		if not self.is_mounted():
			self.output("Mounting share...", verbose_level=2)

			args = [
				"mount", "-t",
				self.connection["protocol"],
				self.connection["mount_url"],
				self.connection["mount_point"],
			]

			self.output(" ".join(args), verbose_level=3)
			subprocess.check_call(args)


	def unmount(self, forced=True):
		"""Try to unmount our mount point.
		Defaults to using forced method.
		Args:
			forced: Bool whether to force the unmount. Default is True.
		"""

		if self.is_mounted():
			cmd = ["/usr/sbin/diskutil", "unmount", self.connection["mount_point"]]

			if forced:
				cmd.insert(2, "force")

			subprocess.check_call(cmd)


	def is_mounted(self):
		"""Test for whether a mount point is mounted.
		If it is currently mounted, determine the path where it's
		mounted and update the connection's mount_point accordingly."""

		self.output("Checking if share is mounted", verbose_level=3)
		was_mounted = False
		mount_check = subprocess.check_output("mount").decode().splitlines()

		for mount in mount_check:

			# Get the source and mount point string between from the end back to the last "on", but
			# before the options (wrapped in parenthesis). Considers alphanumerics,
			# / , _ , - and a blank space as valid, but no crazy chars.
			mount_url_regex = re.compile(r"([\\\w/ -;@$]*) on .*$")
			mount_point_regex = re.compile(r"on ([\w/ -]*) \(.*$")
			mount_url_match = re.search(mount_url_regex, mount)
			mount_url = mount_url_match[1] if mount_url_match else None
			mount_point_match = re.search(mount_point_regex, mount)
			mount_point = mount_point_match[1] if mount_point_match else None

			# Get the mount fs type.
			mount_fs_regex = re.compile(r"\(([\w]*),*.*\)$")
			fs_match = re.search(mount_fs_regex, mount)
			fs_type = fs_match[1] if fs_match else None

			# Does the mount_string match the mount url?
			if (
				mount_url == self.connection["mount_url_passwordless"]
				and self.fs_type == fs_type
				and mount_point
			):

				self.output(
					f"{self.connection['url']} is mounted at {self.connection['mount_point']}",
					verbose_level=3
				)
				was_mounted = True

				if mount_point != self.connection["mount_point"]:
					# Reset the connection's mount point to the discovered value.
					self.connection["mount_point"] = mount_point

				# Found the share, no need to continue.
				break

		if not was_mounted:
			# If the share is not mounted, check for another share mounted to the same path and if
			# found, increment the name to avoid conflicts.
			count = 1
			while os.path.ismount(self.connection["mount_point"]):
				self.connection["mount_point"] = f"{self.connection['mount_point']}-{count}"
				count += 1

		# Do an inexpensive double check...
		return os.path.ismount(self.connection["mount_point"])


	def exists(self, filename):
		"""Report whether a file exists on the share.
		Determines file type by extension.
		Args:
			filename: Filename you wish to check. (No path! e.g.:
				"AdobeFlashPlayer-14.0.0.176.pkg")
		"""
		##### NOT TESTED --  BUT MAY BE USEFUL IN FUTURE UPDATE TO OfflineApps #####
		filepath = os.path.join(self.connection["mount_point"], filename)
		return os.path.exists(filepath)


	def __contains__(self, filename):
		"""Magic method to allow constructs similar to:
			`if 'abc.pkg' in dp:`
		"""
		##### NOT TESTED --  BUT MAY BE USEFUL IN FUTURE UPDATE TO OfflineApps #####
		return self.exists(filename)
