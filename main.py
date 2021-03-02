#!/usr/bin/env python
""" main.py: Provides resolution table from VMware KBs as machine-readable json files.
VMware KBs provide release information only as a human-readable HTML table.
However, for automation it would be nice to have it in a machine-readable format.
This script takes the tables from a VMware KB page and provides a json-file as an output.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Dominik Zorgnotti"
__contact__ = "dominik@why-did-it.fail"
__created__ = "2020-02-26"
__deprecated__ = False
__contact__ = "dominik@why-did-it.fail"
__license__ = "GPLv3"
__status__ = "beta"
__version__ = "0.0.3"

# Imports
from data_handling import create_json_output
from kb_data import KbData
from webparsing import parse_kb_article_ids
import os

# Constants
# VMware master KB article id containing the links to all sub-articles
MASTERKBID = 1014508
# The relative directory where the output it stored (used in GH actions, so beware)
OUTPUTBASEDIR = "outputs"
# The "simple" JSON data orientation types. Index is a bit more tricky as the DF need remodeling.
JSONRECORDS = ["records", "table", "index"]

if __name__ == "__main__":
    # Create output directory
    if not os.path.exists(OUTPUTBASEDIR):
        os.makedirs(OUTPUTBASEDIR)
    vmware_release_kbs = parse_kb_article_ids(MASTERKBID)
    for kb_id in vmware_release_kbs:
        # Pass on the KB id to 0000the data object to fill it
        kb_article = KbData(kb_id=kb_id)
        # Create outputs
        for record_type in JSONRECORDS:
            create_json_output(kb_dataobject=kb_article, output_base_dir=OUTPUTBASEDIR, record_type=record_type)