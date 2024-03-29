#!/usr/bin/env python
""" data_handling.py: Provides resolution table from VMware KBs as machine-readable json files.
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
__version__ = "0.3.0"

import os


def create_json_output(kb_dataobject, output_base_dir: str, record_type: str):
    """Takes a list of dataframes from a KB object, an relative output directory and a JSON data"""
    outputdir = os.path.join(output_base_dir, record_type)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    # TODO Code repeat make this DRY anytime soon
    table_id = 0
    for dataframe in kb_dataobject.list_of_dframes:
        filename = f"kb{kb_dataobject.id}_{kb_dataobject.fmt_product}_table{table_id}_release_as-{record_type}.json"
        if "Build Number" in dataframe.columns and record_type == "index":
            dataframe = transform_index(dataframe)
        # Adding vxrail handling
        elif kb_dataobject.id == 52075 and record_type == "index":
            dataframe = transform_kb52075_index(dataframe)
        try:
            dataframe.to_json(
                f"{outputdir}{os.sep}{filename}",
                indent=4, orient=record_type, date_format="iso"
            )
        except ValueError as err:
            print(f"{kb_dataobject.id}: Error for json {record_type} in table {table_id}: {err}")
        finally:
            table_id += 1
    if kb_dataobject.list_of_merged_frames:
        table_id = 0
        for table_name, dataframe in kb_dataobject.list_of_merged_frames.items():
            filename = f"kb{kb_dataobject.id}_{kb_dataobject.fmt_product}_{table_name}_as-{record_type}.json"
            if "Build Number" in dataframe.columns and record_type == "index":
                dataframe = transform_index(dataframe)
            try:
                dataframe.to_json(
                    f"{outputdir}{os.sep}{filename}",
                    indent=4, orient=record_type, date_format="iso"
                )
            except ValueError as err:
                print(f"{kb_dataobject.id}: Error for json {record_type} in merged table {table_id}: {err}")


def transform_index(dataframe):
    """Takes a dataframe as an input and re-creates the index based on the vxrail release. Destructive to the dataframe
    as duplicates are erased"""
    dataframe.drop_duplicates(subset="Build Number", keep=False, inplace=True)
    dataframe.reset_index(drop=True)
    dataframe.set_index("Build Number", inplace=True)
    return dataframe

def transform_kb52075_index(dataframe):
    """Takes the vxrail dataframe as an input and re-creates the index based on the build number. Destructive to the dataframe
        as duplicates are erased"""
    dataframe.drop_duplicates(subset="VxRail Release", keep=False, inplace=True)
    dataframe.reset_index(drop=True)
    dataframe.set_index("VxRail Release", inplace=True)
    return dataframe

def standardize_columns(dataframe):
    """Takes a dataframe as an input and renames the columns to a common standard"""
    if ("BuildNumber" in dataframe.columns):
        dataframe.rename(columns={"BuildNumber": "Build Number"}, inplace=True)
    if ("Build number" in dataframe.columns):
        dataframe.rename(columns={"Build number": "Build Number"}, inplace=True)
    if "ReleaseDate" in dataframe.columns:
        dataframe.rename(columns={"ReleaseDate": "Release Date"}, inplace=True)
    return dataframe
