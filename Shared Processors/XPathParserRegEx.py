#!/usr/local/autopkg/python
#
# XPathParserRegEx.py Copyright 2022 by Zack Thompson (MLBZ521)
#
# Built from XPathParser, which was inspired by DistributionPkgInfo.py from dataJar
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

"""See docstring for XPathParserRegEx class"""

import os
import re

from xml.etree import ElementTree

from autopkglib import Processor, ProcessorError


__all__ = ["XPathParserRegEx"]


class XPathParserRegEx(Processor):
    """Parses a XML file to pull the desired info using XPath and provides a method to support 
    parsing element attributes via RegEx."""

    description = __doc__

    input_variables = {
        "xml_file": {
            "required": True,
            "description": ("Path to xml file to parse.")
        },
        "xpath_element": {
            "required": True,
            "description": ("XPath element to search for.")
        },
        "xpath_attribute_to_match": {
            "required": True,
            "description": ("In case multiple elements could be found, match "
            "against a specific attribute.")
        },
        "xpath_value_of_attribute_to_match": {
            "required": False,
            "description": ("A (optionally regex) string to find a matching the attribute.")
        },
        "attribute_id_to_return": {
        "required": False,
        "description": ("The attribute of the element desired.")
        },
        "variable_to_assign_attribute_value": {
            "required": False,
            "description": ("The name of the variable to assign the "
                            "value of attribute_id_to_return")
        }
    }

    output_variables = {}


    def main(self):

        # Define variables
        xml_file = self.env["xml_file"]
        xpath_element = self.env["xpath_element"]
        xpath_attribute_to_match = self.env["xpath_attribute_to_match"]
        xpath_value_of_attribute_to_match = self.env["xpath_value_of_attribute_to_match"]
        attribute_id_to_return = self.env["attribute_id_to_return"]
        variable_to_assign_attribute_value = self.env["variable_to_assign_attribute_value"]

        # Verify file exists
        if not os.path.exists(xml_file):
            raise ProcessorError(f"Cannot find the file:  {xml_file}")

        try:
            # Parse the xml file
            tree = ElementTree.parse(xml_file)

            # Find the desired element attribute value
            value = [
                element.attrib[f"{attribute_id_to_return}"] 
                for element in tree.findall(f".//{xpath_element}[@{xpath_attribute_to_match}]") 
                if re.match(rf"{xpath_value_of_attribute_to_match}", element.attrib[f"{xpath_attribute_to_match}"])
            ][0]

        except Exception as error:
            raise ProcessorError(f"Failed to parse the xml file {xml_file}") from error

        if not value:
            raise ProcessorError(f"Unable to determine a value for:  {attribute_id_to_return}")

        self.output(f"attribute_id_to_return:  {value}")
        self.env[variable_to_assign_attribute_value] = value


if __name__ == "__main__":
    PROCESSOR = XPathParserRegEx()
    PROCESSOR.execute_shell()
