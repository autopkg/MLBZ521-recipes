#!/usr/bin/python
#
# 2022 Zack T (mlbz521)
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
"""See docstring for GetMicrosoftOfficeResetOptions class"""

from __future__ import absolute_import

import os
import plistlib
import re
import shlex
import subprocess

from autopkglib import Processor, ProcessorError


__all__ = ["GetMicrosoftOfficeResetOptions"]


class GetMicrosoftOfficeResetOptions(Processor):
    """This processor obtains the choice options from the Office Reset.pkg 
    from Paul Bowden (https://office-reset.com/macadmins/).

    It allows you to ignore specific options, so as not to provide them to 
    your customers.

    The results are passed to the postinstall script the pkg recipe.
    """

    input_variables = {
        "ignore_choices": {
            "description": ( "A comma separated string of choices that will "
                "not be included as selectable options to users. Example:  "
                "com.microsoft.remove.Office, com.microsoft.reset.Outlook"
            ),
            "required": False
        }
    }

    output_variables = {
        "prompt_choices": {
            "description": "The list of choices that the postinstall script "
            "will prompt with."
        },
    }

    description = __doc__


    def execute_process(self, command, input=None):
        """
        A helper function for subprocess.

        Args:
            command (str):  The command line level syntax that would be written in a 
                shell script or a terminal window

        Returns:
            dict:  Results in a dictionary
        """

        # Validate that command is not a string
        if not isinstance(command, str):
            raise TypeError("Command must be a str type")

        # Format the command
        command = shlex.split(command)

        # Run the command
        process = subprocess.Popen( command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
            shell=False, universal_newlines=True )

        if input:
            (stdout, stderr) = process.communicate(input=input)

        else:
            (stdout, stderr) = process.communicate()

        return {
            "stdout": (stdout).strip(),
            "stderr": (stderr).strip() if stderr != None else None,
            "exitcode": process.returncode,
            "success": True if process.returncode == 0 else False
        }


    def main(self):
        """Find the latest receipt that contains all 
            the information we're looking for.

        Raises:
            ProcessorError: Package does not exist at the path found.
            ProcessorError: Unable to create or locate Choice XML.
            ProcessorError: No choices found in the choice.plist file.
            ProcessorError: Failed to match choices.
        """

        pkg_path = self.env.get("pathname")
        ignore_choices = self.env.get("ignore_choices").split(",")
        self.output("Choices to ignore:  {}".format(ignore_choices), verbose_level=2)

        if not os.path.exists(pkg_path):
            raise ProcessorError("Unable to locate the downloaded .pkg!")

        results = self.execute_process(
            "/usr/sbin/installer -showChoiceChangesXML -pkg {} -target /".format(
                pkg_path))

        if not results["success"]:
            raise ProcessorError("Failed to obtain the available choices from the pkg!")

        plist_contents = plistlib.loads(results["stdout"].encode("utf-8"))

        choices = {
            choice.get("choiceIdentifier")
            for choice in plist_contents
        }

        if not choices:
            raise ProcessorError("Failed to identify possible choices!")

        self.output("Found choices:\n{}".format(choices), verbose_level=3)

        # reset_choices = set()
        # remove_choices = set()
        available_choices = set()

        for choice in choices:
            if choice not in ignore_choices:

                if re.match(r"com.microsoft.reset.Factory", choice):
                    available_choices.add("Factory Reset All Apps")
                    self.output("Found choice for Factory Reset:  {}".format(choice), verbose_level=3)

                elif re.match(r"com.microsoft.remove.Outlook.Data", choice):
                    available_choices.add("Remove Outlook Data")
                    self.output("Found choice for Remove Outlook Data:  {}".format(choice), verbose_level=3)

                elif re.match(r"com.microsoft.reset.+", choice):
                    # reset_choices.add(choice.split("com.microsoft.reset.")[1])
                    available_choices.add(re.sub(r"com.microsoft.reset.", "Reset ", choice))
                    self.output("Found reset choice:  {}".format(choice), verbose_level=3)

                elif re.match(r"com.microsoft.remove.+", choice):
                    # remove_choices.add(choice.split("com.microsoft.remove.")[1])
                    available_choices.add(re.sub(r"com.microsoft.remove.", "Remove ", choice))
                    self.output("Found remove choice:  {}".format(choice), verbose_level=3)

        # if reset_choices or remove_choices:
        if not available_choices:
            raise ProcessorError("Failed to match choices!")

        prompt_choices = "\n".join(sorted(available_choices, reverse=True))
        self.env["prompt_choices"] = prompt_choices
        self.output("Prompt Choice Options:\n{}".format(prompt_choices), verbose_level=3)


if __name__ == "__main__":
    PROCESSOR = GetMicrosoftOfficeResetOptions()
    PROCESSOR.execute_shell()
