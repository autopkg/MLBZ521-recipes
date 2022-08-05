#!/usr/local/autopkg/python
#
# InputVariableTextSubstituter.py
# Copyright 2021 by Zack Thompson (MLBZ521)
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

from __future__ import absolute_import

import re

from autopkglib import Processor, ProcessorError

__all__ = ["InputVariableTextSubstituter"]


class InputVariableTextSubstituter(Processor):

    """This processor substitutes character(s) in a string with either 
    another string or the value of a set autopkg variable and then returns
    the modified string as a supplied variable.

    I wrote it to be able to substitute values into an input variable for 
    when you want to use, for example the version in an input variable, 
    but the version variable has not been set yet, not until the (child) 
    recipe runs.  However, it can be used to substitute strings in any 
    other strings.
    """

    description = __doc__

    input_variables = {
        "original_string": {
            "required": True,
            "description": "The original string that needs to be edited."
        },
        "string_to_replace": {
            "required": True,
            "description": "The old character(s) to be replaced in the "
                           "original string."
        },
        "replacement_string": {
            "required": False,
            "description": "The new character(s) that will replace the "
                           "old string."
        },
        "variable_to_use": {
            "required": False,
            "description": "Instead of replacing strings with strings, "
                            "replace the original string with the value "
                            "of an autopkg variable."
        },
        "return_variable": {
            "required": True,
            "description": ("The name of the variable to assign the "
                            "result of the modified string too.")
        },
        "append_space": {
            "required": False,
            "type":  "Boolean",
            "default":  False,
            "description": ("Append a space before the replacement string or "
                            "variable.  Default is False")
        }
    }
    output_variables = {
        "return_variable": {
            "description": "The name variable that was set."
        },
        "return_variable_value": {
            "description": "The variable value that was set."
        }
    }


    def main(self):

        if self.env.get("replacement_string") and self.env.get("variable_to_use"):
              raise ProcessorError("Both of the input variables 'replacement_string' or 'variable_to_use' were set!")

        elif self.env.get("replacement_string"):
            replacement = self.env.get("replacement_string")

        elif self.env.get("variable_to_use"):
            replacement = self.env.get(self.env.get("variable_to_use"))

        else:
            raise ProcessorError("Neither of the input variables 'replacement_string' or 'variable_to_use' were set!")

        original_string = self.env.get("original_string")
        string_to_replace = self.env.get("string_to_replace")
        return_variable = self.env.get("return_variable")

        if self.env.get("append_space"):
            replacement = " {}".format(replacement)

        new_string = re.sub(string_to_replace, replacement, original_string)

        self.env[return_variable] = new_string
        self.env["return_variable_value"] = new_string
        self.output("{}: {}".format(return_variable, self.env[return_variable]))

        # For back to back runs of this processor...
        for variable in ( "replacement_string", "variable_to_use", "append_space" ):
            self.env[variable] = ""


if __name__ == "__main__":
    processor = InputVariableTextSubstituter()
    processor.execute_shell()
