#!/usr/local/autopkg/python

"""See docstring for DownloadMATLABProcessor class"""

import os.path
import re
import subprocess

from xml.etree import ElementTree

from autopkglib import Processor, ProcessorError


__all__ = ["DownloadMATLABProcessor"]


class DownloadMATLABProcessor(Processor):

	"""This processor builds a Managed Frameworks package."""

	description = __doc__
	input_variables = {
		"mpm_path": {
			"required": False,
			"description": "The path to the MATLAB `mpm` CLI utility.",
		},
		"dl_version": {
			"required": False,
			"description": (
				"Optionally specify version of MATLAB to download, "
				"otherwise the latest release will be downloaded."
			)
		},
		"dl_products": {
			"required": False,
			"description": (
				"The MATLAB 'products' to download.  "
				"This can include MATLAB, additional products, and support packages."
			),
		},
		"dl_archs": {
			"required": False,
			"description": (
				"The architecture to download for.  Technically, in addition to "
				"macOS Intel/ARM, this can support Windows and Linux as well."
			),
		},
		"installer_input_file": {
			"required": False,
			"description": "A variable file used instead of the `dl_<...>` variables.",
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

		if not (mpm_path := self.env.get("mpm_path")):
			raise ProcessorError("The path to `mpm` was not provided.")

		# Get environment variables
		dl_version = self.env.get("dl_version", "MATLAB")
		dl_products = self.env.get("dl_products", "MATLAB")
		dl_archs = self.env.get("dl_archs", "maca64 maci64")
		installer_input = self.env.get("INSTALLER_INPUT")
		installer_input_file = self.env.get("installer_input_file")
		RECIPE_CACHE_DIR = self.env.get("RECIPE_CACHE_DIR")

		# Define local variables
		recipe_cache_download_dir = os.path.join(RECIPE_CACHE_DIR, "downloads")

		self.output(f"Downloading MATLAB content:\n\tRelease:  {dl_version}\n\tProducts:  {dl_products}\n\tPlatforms:  {dl_archs}", verbose_level=1)

		if installer_input_file:
			mpm_cmd = f"{mpm_path} download --inputfile={installer_input_file}"
			products = re.findall(r"\n(?<![#])\s*product\.(.+)", installer_input)
			self.output(f"{products = }", verbose_level=3)
		elif dl_version and dl_archs and dl_products:
			mpm_cmd = f"{mpm_path} download --release='{dl_version}' --destination='{recipe_cache_download_dir}/installer_content' --platforms={dl_archs} --products={dl_products}"
		else:
			raise ProcessorError("Required arguments were not provided.")

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
		self.env["products_to_install"] = " ".join(products)
		self.env["pathname"] = installer_app
		self.env["download_changed"] = True


if __name__ == "__main__":
	PROCESSOR = DownloadMATLABProcessor()
	PROCESSOR.execute_shell()
