#!/usr/bin/env python
#
# Copyright 2020 Zack Thompson (MLBZ521)
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

import xml.etree.ElementTree as ET
from autopkglib import Processor, ProcessorError

__all__ = ["PhETLabSimulationsProcessor"]

class PhETLabSimulationsProcessor(Processor):

    """This processor provides the attributes for supported PhET Lab Simulations."""

    input_variables = {
        "lab_sim": {
            "required": True,
            "description": "Which Maples Major Version to look for available patches."
        }
    }
    output_variables = {
        "version_url": {
            "description": "Returns the url where to search for the version number."
        },
        "download_url": {
            "description": "Returns the url to download."
        },
        "bundle_id_string": {
            "description": "Returns the postfix string to use for the bundle identifier."
        },
        "png_icns_file_name": {
            "description": "Returns the name of the .png and .icns files."
        },
        "lab_description": {
            "description": "Returns a description of the lab to use in Self Service."
        }
    }

    description = __doc__

    def main(self):

        # Define variables
        lab_sim = self.env.get('lab_sim')
        if not lab_sim:
            raise ProcessorError(
                "A value for 'lab_sim' is required, but none is set!")
        else:
            self.output('Searching for lab simulation:  {}'.format(lab_sim))

        if lab_sim == "Balloons and Buoyancy":
            version_url = 'https://phet.colorado.edu/en/simulation/legacy/balloons-and-buoyancy'
            download_url = 'https://phet.colorado.edu/sims/ideal-gas/balloons-and-buoyancy_en.jar'
            bundle_id_string = "balloons-and-buoyancy"
            png_icns_file_name = "BalloonsAndBuoyancy"
            lab_description = "Experiment with a helium balloon, a hot air balloon, or a rigid sphere filled with different gases.  Discover what makes some balloons float and others sink.\nSample Learning Goals\n* Determine what causes the the balloon, rigid sphere, and helium balloon to rise up or fall down in the box.\n* Predict how changing a variable among P, V, T, and number influences the motion of the balloons."

        # elif lab_sim == "":
        #     version_url = ''
        #     download_url = ''
        #     bundle_id_string = ""
        #     png_icns_file_name = ""
        #     lab_description = ""

        else:
            raise ProcessorError('This lab simulation is not yet supported:  {lab_sim}.\
\
Feel free to submit a pull request to add submit.'.format(lab_sim=lab_sim))


        # Return values
        self.env["version_url"] = version_url
        self.output("version_url URL: {}".format(self.env["version_url"]))
        self.env["download_url"] = download_url
        self.output("Download URL: {}".format(self.env["download_url"]))
        self.env["bundle_id_string"] = bundle_id_string
        self.output("BundleID String: {}".format(self.env["bundle_id_string"]))
        self.env["png_icns_file_name"] = png_icns_file_name
        self.output("File Name of .icns and .png: {}".format(self.env["png_icns_file_name"]))
        self.env["lab_description"] = lab_description
        self.output("Lab Description: {}".format(self.env["lab_description"]))


if __name__ == "__main__":
    processor = PhETLabSimulationsProcessor()
    processor.execute_shell()
