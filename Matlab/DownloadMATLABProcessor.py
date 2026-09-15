#!/usr/local/autopkg/python

"""See docstring for DownloadMATLABProcessor class"""

import json
import os.path
import re
import subprocess

from html.parser import HTMLParser
from xml.etree import ElementTree

import requests

from autopkglib import Processor, ProcessorError


__all__ = ["DownloadMATLABProcessor"]


class TargetTextExtractor(HTMLParser):
	def __init__(self, target_tag, attr_key, attr_value):
		super().__init__()
		self.target_tag = target_tag
		self.in_target_tag = False
		self.extracted_content = []
		self.attr_key = attr_key
		self.attr_value = attr_value
	def handle_starttag(self, tag, attributes):
		if tag == self.target_tag:
			if self.attr_key and self.attr_value:
				for key, value in attributes:
					if key == self.attr_key and value == self.attr_value :
						self.in_target_tag = True
			else:
				self.in_target_tag = True
	def handle_endtag(self, tag):
		# Turn off flag when the target tag closes
		if tag == self.target_tag:
			self.in_target_tag = False
	def handle_data(self, data):
		# Capture the text if we are currently inside the target tag
		if self.in_target_tag:
			self.extracted_content.append(data)
	def get_results(self):
		return self.extracted_content


class DownloadMATLABProcessor(Processor):

	"""This processor builds a Managed Frameworks package."""

	description = __doc__
	input_variables = {
		"mpm_path": {
			"required": False,
			"description": (
				"Optionally specify version of MATLAB to download, "
				"otherwise the latest release will be downloaded."
			)
		},
		"dl_version": {
			"required": False,
			"description": (
				"Optionally specify version of MATLAB to download, "
				"otherwise the latest release will be downloaded."
			)
		},
		"installer_input_config": {
			"required": False,
			"description": "A dictionary describing `mpm` arguments and values.",
		}
	}
	output_variables = {
		"version": {
			"description": "Full version string (i.e. major version "
				"plus update level; aka minor version)."
		},
		"major_version": {
			"description": "Major release version string."
		},
		"pathname": {
			"description": "Path to the downloaded content."
		},
		"products_to_install": {
			"description": ("The list of products that were downloaded.  "
				"This will be used with `mpm install` to install these products.")
		}
	}

	def execute_process(self, command, input=None):
		"""
		A helper function for subprocess.

		Args:
			command (str):  The command line level syntax that would be
				written in shell or a terminal window.
		Returns:
			Results in a dictionary.
		"""

		# Validate that command is not a string
		if not isinstance(command, str):
			raise TypeError("Command must be a str type")

		# Run the command
		process = subprocess.Popen(
			command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)

		if input:
			(stdout, stderr) = process.communicate(input=bytes(input, "utf-8"))
		else:
			(stdout, stderr) = process.communicate()

		return {
			"stdout": (stdout.decode()).strip(),
			"stderr": (stderr.decode()).strip() if stderr != None else None,
			"status": process.returncode,
			"success": True if process.returncode == 0 else False,
			"process": process
		}


	def main(self):

		# Get environment variables
		mpm_path = self.env.get("mpm_path")
		dl_version = self.env.get("dl_version")
		installer_input_config = self.env.get("INSTALLER_INPUT_CONFIG")
		remove_unsupported_pkgs = self.env.get("remove_unsupported_pkgs")
		RECIPE_CACHE_DIR = self.env.get("RECIPE_CACHE_DIR")

		# Define local variables
		recipe_cache_download_dir = os.path.join(RECIPE_CACHE_DIR, "downloads")
		installer_input_file = f"{recipe_cache_download_dir}/installer_input.txt"

		if not dl_version:
			# If a version wasn't provided to download, then get the latest from
			# the available list of input_files on GitHub
			github_input_files_url = "https://github.com/mathworks-ref-arch/matlab-dockerfile/tree/main/mpm-input-files"
			github_input_files = requests.get(github_input_files_url)

			parser = TargetTextExtractor(
				target_tag="script", attr_key="data-target", attr_value="react-app.embeddedData")
			parser.feed(github_input_files.text)
			parser.get_results()

			versions = json.loads(
				parser.get_results()[0]).get("payload").get("codeViewTreeRoute").get("tree").get("items")

			# Get the latest from the list
			dl_version = versions[-1].get("name")

		# Get the input_file itself
		input_file_url = f"https://raw.githubusercontent.com/mathworks-ref-arch/matlab-dockerfile/refs/heads/main/mpm-input-files/{dl_version}/mpm_input_{dl_version.lower()}.txt"
		input_file_text = (requests.get(input_file_url).text)
		self.output(f"MPM Input File:  {input_file_text}", verbose_level=4)

		search_pattern = ".*?download\.(.*?)(?=\n+#{72})"

		# Get the available "Products" from the input file
		if products := re.search("## PRODUCTS" + search_pattern, input_file_text, re.DOTALL):
			available_products = products.group(1)
			self.output(f"Available Products:  {available_products}", verbose_level=4)

		# Get the available "Support Packages" from the input file
		if packages := re.search("## SUPPORT PACKAGES" + search_pattern, input_file_text, re.DOTALL):
			available_support_packages = packages.group(1)
			self.output(f"Available Support Packages:  {available_support_packages}",
				verbose_level=4)

		if features := re.search("## OPTIONAL FEATURES" + search_pattern, input_file_text, re.DOTALL):
			available_optional_features = features.group(1)
			self.output(f"Available Optional Features:  {available_optional_features}",
				verbose_level=4)

		# Get the version specific checksum
		checksum = re.search("\?checksum=.*\w", input_file_text, re.DOTALL).group(0)

		# Build the input_file that will be needed in next steps
		final_installer_input_config = f"{checksum}\ndestinationFolder={recipe_cache_download_dir}/installer_content\n"
		products = ""
		support_packages = ""
		optional_features = ""

		# Loop through the user provided items and set the
		# values if defined, otherwise use the defaults
		for key, value in installer_input_config.items():

			if key == "platforms":
				if isinstance(value, list):
					platforms = " ".join(value)
					final_installer_input_config += "\n".join("platform." + item for item in value)
				else:
					platforms = value
					final_installer_input_config += f"\nplatform.{value}"

				final_installer_input_config += "\n"

			elif key == "products" and value:
				if value == "all":
					products = re.sub("\n?# ?product\.", " ", available_products)
					final_installer_input_config += re.sub("# ?", "", available_products)
				elif value:
					products += value
					final_installer_input_config += value

			elif key == "support_packages":
				if value == "all":
					final_installer_input_config += re.sub("# ?", "", available_support_packages)
					support_packages += re.sub("# ?product\.", "", available_support_packages)
				elif value:
					final_installer_input_config += value
					support_packages += value

			elif key == "optional_features":
				if value == "all":
					final_installer_input_config += re.sub("# ?", "", available_optional_features)
					optional_features += re.sub("# ?product\.", "", available_support_packages)
				elif value:
					final_installer_input_config += value
					optional_features += value

			else:
				final_installer_input_config += f"{key}={value}\n"

		# Write the file to disk
		with open(installer_input_file, "w", encoding="utf-8") as f:
			f.write(final_installer_input_config)

		products = products.strip()
		support_packages = support_packages.strip()
		optional_features = optional_features.strip()

		self.output(
			f"Downloading MATLAB content:\n\tRelease:  {dl_version}\n\tPlatforms:  {platforms}\n"
			f"\tProducts:  {products}\n\tSupport Packages:  {support_packages}\n"
			f"\tOptional Features:  {optional_features}\n",
			verbose_level=1)

		# if installer_input_file:
		if dl_version and platforms and products:
			mpm_cmd = f"{mpm_path} download --inputfile={installer_input_file}"
		else:
			raise ProcessorError("Required arguments were not provided.")

		self.output(f"Executing cmd:  {mpm_cmd}", verbose_level=1)
		mpm_download_results = self.execute_process(mpm_cmd)

		if remove_unsupported_pkgs and \
			"Error: The following products are not supported on the specified platforms:" in mpm_download_results['stderr']:

			self.output(f"Removing unsupported packages...", verbose_level=1)
			unsupported_pkgs = mpm_download_results['stderr'].split("\n")

			for unsupported_pkg in unsupported_pkgs:
				final_installer_input_config = re.sub(f"product.{unsupported_pkg}\n", "", final_installer_input_config, re.DOTALL)
				products = re.sub(f"{unsupported_pkg}", "", products, re.DOTALL)

			# Write the file to disk
			with open(installer_input_file, "w", encoding="utf-8") as f:
				f.write(final_installer_input_config)

			self.output(f"Executing cmd:  {mpm_cmd}", verbose_level=1)
			mpm_download_results = self.execute_process(mpm_cmd)

		self.output(f"Results:\n\tExit Code:  {mpm_download_results['status']}\n\tOutput:\n```\n{mpm_download_results['stdout']}\n```", verbose_level=3)

		if not mpm_download_results["success"]:
			raise ProcessorError(f"Error encountered:\n{mpm_download_results['stderr']}")

		self.output("Download complete!", verbose_level=1)

		installer_app = f"{recipe_cache_download_dir}/installer_content.app"
		product_info = f"{installer_app}/ProductFilesInfo.xml"

		self.output(f"Installer app path:  {installer_app}", verbose_level=1)

		# Verify file exists
		if not os.path.exists(product_info):
			raise ProcessorError(f"Cannot find the file:  {product_info}")

		# Parse the xml file
		tree = ElementTree.parse(product_info)

		# Find the desired element and its attribute(s)
		try:
			update_level = tree.findtext("update_level")
			release = tree.findtext("release")

		except Exception as error:
				raise ProcessorError(f"Can't parse xml file {product_info}: {error}") from error

		if update_level == 0:
			self.env["version"] = dl_version
		else:
			self.env["version"] = f"{dl_version}_u{update_level}"

		self.env["major_version"] = release
		self.env["products_to_install"] = products
		self.env["pathname"] = installer_app
		self.env["download_changed"] = True


if __name__ == "__main__":
	PROCESSOR = DownloadMATLABProcessor()
	PROCESSOR.execute_shell()
