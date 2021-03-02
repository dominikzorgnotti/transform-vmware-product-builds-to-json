import os
import pandas as pd


def create_json_output(kb_dataobject, output_base_dir: str, record_type: str):
    """Takes a list of dataframes from a KB object, an relative output directory and a JSON data"""
    outputdir = os.path.join(output_base_dir, record_type)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    table_id = 0
    for dataframe in kb_dataobject.list_of_dframes:
        filename = f"kb{kb_dataobject.id}_{kb_dataobject.fmt_product}_table{table_id}_release_as-{record_type}.json"
        if "Build Number" in dataframe.columns and record_type == "index":
            dataframe = transform_index(dataframe)
        dataframe.to_json(
            f"{outputdir}{os.sep}{filename}",
            indent=4, orient=record_type, date_format="iso"
        )
        table_id += 1


def transform_index(dataframe):
    """Takes a dataframe as an input and re-creates the index based on the build number. Destructive to the dataframe
    as duplicates are erased"""
    dataframe.drop_duplicates(subset="Build Number", keep=False, inplace=True)
    dataframe.reset_index(drop=True)
    dataframe.set_index("Build Number", inplace=True)
    return dataframe
