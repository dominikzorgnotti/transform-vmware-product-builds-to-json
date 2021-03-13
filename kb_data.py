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

import pandas as pd

from webparsing import get_kb_webdata

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
        dict_of_releases = {}
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
            list_of_release_df.append(releaseinfo_dataframe)
            # Fun stuff may happen with dataframes if not erased before the next iteration
            del current_df, releaseinfo_dataframe
        return list_of_release_df


# You might read this and say "he's drunk!". Alas, it's pure desperation.

#vCenter releases
class Kb2143838(KbData):
    def __init__(self, kb_id):
        super().__init__(kb_id)
        self.list_of_dframes = self.parse_releasedata()
        self.list_of_merged_frames = self.merge_tables_kb2143838()

    def parse_releasedata(self):
        """Accepts the html data for product releases from the KB article for parsing with pandas."""
        df = pd.read_html(self.raw_html_resolution, flavor="bs4")
        # Contains a list of all tables converted to dataframes in the resolution section
        list_of_release_df = []
        for table_id in range(len(df)):
            if table_id == 0:
                vcenter7_table = df[table_id]
                reformatted_df = self.transform_kb2143838(vcenter7_table)
                reformatted_df["Edition"] = "VCSA"
                reformatted_df["Release Date"] = pd.to_datetime(reformatted_df["Release Date"], infer_datetime_format=True,
                                                            errors='coerce')
                list_of_release_df.append(reformatted_df)
            elif table_id == 1:
                vcenter67_table = df[table_id]
                product_editions = ["VCSA", "Windows"]
                for product_edition in product_editions:
                    split_df = self.split_kb2143838(vcenter67_table, product_edition)
                    reformatted_df = self.transform_kb2143838(split_df)
                    reformatted_df["Release Date"] = pd.to_datetime(reformatted_df["Release Date"],
                                                                    infer_datetime_format=True,
                                                                    errors='coerce')
                    list_of_release_df.append(reformatted_df)
                    del split_df
            elif table_id == 2:
                # The HTML table have no header, we need to reassign the first row as heading
                df_header = df[table_id][:1]
                current_df = df[table_id][1:]
                current_df.columns = df_header.values.tolist()[0]
                # Moving the del up here
                del df_header
                current_df["Edition"] = "Windows"
                # Get the data types right, especially the date format='%m/%d/%Y'
                current_df["Release Date"] = pd.to_datetime(current_df["Release Date"], infer_datetime_format=True, errors='coerce')
                list_of_release_df.append(current_df)
            else:
                print("Unknown table added, please add handling")
        return list_of_release_df

    def split_kb2143838(self, dataframe, product_edition):
        """Splits a dataframe based on the product edition (VCSA, Windows) and returns the output dataframe"""
        tempdf_headless = dataframe[dataframe[0] == product_edition]
        tempdf_header = tempdf_headless[:1]
        tempdf = tempdf_headless[1:]
        tempdf.columns = tempdf_header.values.tolist()[0]
        tempdf.rename(columns={product_edition: "Edition"}, inplace=True)
        return tempdf

    def transform_kb2143838(self, dataframe):
        """Special handling of KB2143838 (vCenter)"""
        # When you access the vCenter API the values from this column are returned, alias it as Build Number
        if "Client/MOB/vpxd.log" in dataframe.columns:
            dataframe["Build Number"] = dataframe["Client/MOB/vpxd.log"]
        if "Version" in dataframe.columns:
            dataframe["Version"].str.strip(u" ")
            tempdf = dataframe.rename(columns={"Version": "Version - Release Name"})
            tempdf[["Version", "Release Name"]] = tempdf["Version - Release Name"].str.split(pat=r"(", expand=True)
            tempdf["Release Name"] = tempdf["Release Name"].str.strip(r")")
        return tempdf

    def merge_tables_kb2143838(self):
        """merge table operations"""
        merged_vcenter_tables = []
        # Prepare the tables
        vc7x_vcsa = self.list_of_dframes[0]
        vc67_vcsa = self.list_of_dframes[1]
        vc67_win = self.list_of_dframes[2]
        vc_win_only = self.list_of_dframes[3]
        #Merge VCSA tables
        vcsa_builds = vc7x_vcsa.append(vc67_vcsa)
        vcsa_builds.reset_index(drop=True)
        vcsa_builds.set_index("Build Number", inplace=True)
        merged_vcenter_tables.append(vcsa_builds)
        #Merge vCenter for Windows tables
        windows_builds = vc67_win.append(vc_win_only)
        windows_builds.reset_index(drop=True)
        windows_builds.set_index("Build Number", inplace=True)
        merged_vcenter_tables.append(windows_builds)
        #Merge both tables
        vc_all_builds = vcsa_builds.append(windows_builds)
        merged_vcenter_tables.append(vc_all_builds)
        # Return the list
        return merged_vcenter_tables

#vRA releases
class Kb2143850(KbData):
    def __init__(self, kb_id):
        super().__init__(kb_id)
        self.list_of_dframes = self.parse_releasedata()

    def parse_releasedata(self):
        """Accepts the html data for product releases from the KB article for parsing with pandas."""
        df = pd.read_html(self.raw_html_resolution, flavor="bs4")
        # Contains a list of all tables converted to dataframes in the resolution section
        list_of_release_df = []
        for table_id in range(len(df)):
            if table_id == 0:
                # The HTML table have no header, we need to reassign the first row as heading
                df_header = df[table_id][:1]
                current_df = df[table_id][1:]
                current_df.columns = df_header.values.tolist()[0]
                # Moving the del up here
                del df_header
                current_df = self.transform_kb2143850(current_df)
                # Get the data types right, especially the date format='%m/%d/%Y'
                current_df["Release Date"] = pd.to_datetime(current_df["Release Date"], infer_datetime_format=True,
                                                            errors='coerce')
                list_of_release_df.append(current_df)
            else:
                print("Unknown table added, please add handling")
        return list_of_release_df

    def transform_kb2143850(self, dataframe):
        """Special handling of KB2143850 (vRA)"""
        if r"Build Number - Version" in dataframe:
            dataframe[["Build Number", "Version"]] = dataframe[r"Build Number - Version"].str.split(r" - ", expand=True)
        return dataframe