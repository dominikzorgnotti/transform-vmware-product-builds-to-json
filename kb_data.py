#!/usr/bin/env python
""" kb_data.py: Provides resolution table from VMware KBs as machine-readable json files.
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



from webparsing import get_kb_webdata
import html5lib
import pandas as pd

# YOLO as I am okay with overwriting DF data regardless of the results
pd.options.mode.chained_assignment = None  # default='warn'


class KbData:

    def __init__(self, kb_id):
        self.id = kb_id
        self.raw_html_article = get_kb_webdata(kb_id)
        self.title = self.get_title()
        self.product = self.get_first_product_name()
        self.fmt_product = self.format_product_name()
        self.raw_html_resolution = self.get_resolution_section()
        self.list_of_dframes = self.parse_releasedata()
        self.list_of_merged_frames = None

    def get_resolution_section(self):
        """Extracts the resolution section from the KB article content section"""
        # Get the Section within the webpage that holds the desired data (make it a bit more targeted)
        if "Resolution" in self.raw_html_article["content"][1]:
            resolution = self.raw_html_article["content"][1]["Resolution"]
        elif "Resolution" in self.raw_html_article["content"][0]:
            resolution = self.raw_html_article["content"][0]["Resolution"]
        else:
            raise ValueError("No resolution section in this page!")
        return resolution

    def get_first_product_name(self):
        """Extracts the first product mentioned in the KB articles meta data"""
        # Get the product, quick win - just pick the first in the list
        return self.raw_html_article["meta"]["articleProducts"]["relatedProducts"][0]

    def format_product_name(self):
        """Makes a lower-case-version without spaces from the product name and returns it as a string"""
        return self.product.lower().strip().replace(" ", "_")

    def get_title(self):
        """Extracts the first product mentioned in the KB articles meta data"""
        # Get the product, quick win - just pick the first in the list
        return self.raw_html_article["meta"]["articleInfo"]["title"]

    def parse_releasedata(self):
        """Accepts the html data for product releases from the KB article for parsing with pandas."""
        df = pd.read_html(self.raw_html_resolution, flavor="bs4")
        # Contains a list of all tables converted to dataframes in the resolution section
        list_of_release_df = []
        for table_id in range(len(df)):
            # Since some HTML table have no header, we need to reassign the first row as heading
            if "Version" not in df[table_id].columns:
                df_header = df[table_id][:1]
                current_df = df[table_id][1:]
                current_df.columns = df_header.values.tolist()[0]
                # Moving the del up here
                del df_header
            else:
                current_df = df[table_id]
            releaseinfo_dataframe = current_df
            # Get the data types right, especially the date format='%m/%d/%Y'
            if "Release Date" in current_df.columns:
                releaseinfo_dataframe["Release Date"] = pd.to_datetime(current_df["Release Date"],
                                                                       infer_datetime_format=True, errors='coerce')
            # Skipping build number conversion. This produces non-deterministic results atm
            # if "Build Number" in current_df.columns:
            #     releaseinfo_dataframe["Build Number"] = pd.to_numeric(current_df["Build Number"],
            #                                                           errors='coerce', downcast="integer")
            list_of_release_df.append(releaseinfo_dataframe)
            # Fun stuff may happen with dataframes if not erased before the next iteration
            del current_df, releaseinfo_dataframe
        return list_of_release_df
