#!/usr/bin/env python
""" webparsing.py: Provides resolution table from VMware KBs as machine-readable json files.
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
__version__ = "0.2.0"

import requests, re
from bs4 import BeautifulSoup

BASEURL_VMWARE_KB = "https://kb.vmware.com/services/apexrest/v1/article?docid="


def get_kb_webdata(kb_article_id: int):
    """Accepts an int with the KB article id and will return the wbe response as JSON output"""
    vmware_kb_url = f"{BASEURL_VMWARE_KB}{str(kb_article_id)}"
    response = requests.get(vmware_kb_url)
    response.raise_for_status()
    return response.json()


def parse_kb_article_ids(summary_kb_article: int):
    """Accepts an int with the KB article id holding the sub-pages with the release data. Returns these as list of int"""
    raw_data = get_kb_webdata(summary_kb_article)
    list_of_kb_ids = []
    resolution = raw_data["content"][1]["Resolution"]
    # Parse for anchor tags in the table of the resolution table
    soup = BeautifulSoup(resolution, "html.parser")
    table = soup.find("table")
    anchors = table.find_all("a")
    # A very crude way of extracting the KB id from the HREF since not all are in the same format :-(
    regular_expression = r"/(\d+)(?:.*)"
    regex_object = re.compile(regular_expression)
    for href_link in anchors:
        regex_results = regex_object.search(href_link["href"])
        kb_id = regex_results.groups()[0]
        list_of_kb_ids.append(int(kb_id))
    return list_of_kb_ids
