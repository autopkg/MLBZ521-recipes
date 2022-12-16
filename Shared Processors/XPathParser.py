#!/usr/local/autopkg/python
#
# Copyright 2022 Zack Thompson (MLBZ521)
#
# Inspired by DistributionPkgInfo.py from dataJar
#   https://github.com/autopkg/dataJAR-recipes/blob/master/Shared%20Processors/DistributionPkgInfo.py
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

"""See docstring for XPathParser class"""

import os.path
from xml.etree import ElementTree

from autopkglib import Processor, ProcessorError

__all__ = ["XPathParser"]


class XPathParser(Processor):
    """Parses a XML file to pull the desired info using XPath."""

    description = __doc__
    input_variables = {
        "xml_file": {
            "required": True,
            "description": "Path to xml file to parse."
        },
        "xpath": {
            "required": True,
            "description": ("XPath string to search for.  Only the "
                            "first result is returned if there are "
                            "multiple matches")
        },
        "attribute_one": {
            "required": True,
            "description": "Attribute to get the value from."
        },
        "attribute_two": {
            "required": False,
            "description": "A second attribute to get the value from."
        },
        "return_variable_attribute_one": {
            "required": False,
            "description": ("The name of the variable to assign the "
                            "value of attribute_one")
        },
        "return_variable_attribute_two": {
            "required": False,
            "description": ("The name of the variable to assign the "
                            "value of attribute_two")
        }
    }
    output_variables = {}


    def main(self):

        # Define variables
        xml_file = self.env["xml_file"]
        xpath = self.env["xpath"]
        attribute_one = self.env["attribute_one"]
        return_variable_one = self.env["return_variable_attribute_one"]

        # Check if a second attribute was desired
        try:
            attribute_two = self.env["attribute_two"]
            return_variable_two =self.env["return_variable_attribute_two"]
        except Exception:
            attribute_two = None
            return_variable_two = None

        # Verify file exists
        if not os.path.exists(xml_file):
            raise ProcessorError(f"Cannot find the file:  {xml_file}")

        # Parse the xml file
        tree = ElementTree.parse(xml_file)

        # Find the desired element and its attribute(s)
        try:
            xml_info = tree.findall(xpath)[0]
            value_one = xml_info.get(attribute_one)

            if attribute_two != None:
                value_two = xml_info.get(attribute_two)

        except Exception as error:
                raise ProcessorError(f"Can't parse xml file {xml_file}: {error}") from error

        if not value_one:
            raise ProcessorError(f"Unable to determine a value for:  {attribute_one}")

        self.output(f'attribute_one:  {value_one}')
        self.env[return_variable_one] = value_one

        if attribute_two != None:
            if not value_two:
                raise ProcessorError(f"Unable to determine a value for:  {attribute_two}")

            self.output(f'attribute_two:  {value_two}')
            self.env[return_variable_two] = value_two


if __name__ == '__main__':
    PROCESSOR = XPathParser()
    PROCESSOR.execute_shell()
