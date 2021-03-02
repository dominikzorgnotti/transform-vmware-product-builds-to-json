import os
import pandas as pd


### This could be consolidated into one function but let's keep em separated to allow for more flexibility


def create_json_output(kb_dataobject, output_base_dir: str, record_type: str):
    outputdir = os.path.join(output_base_dir, record_type)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    table_id = 0
    for dataframe in kb_dataobject.list_of_dframes:
        filename = f"kb{kb_dataobject.id}_{kb_dataobject.fmt_product}_table{table_id}_release_as-{record_type}.json"
        dataframe.to_json(
            f"{outputdir}{os.sep}{filename}",
            indent=4, orient=record_type, date_format="iso"
        )
        table_id += 1


def create_json_index(kb_dataobject, output_base_dir: str):
    record_type = "index"
    outputdir = os.path.join(output_base_dir, record_type)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    table_id = 0
    for dataframe in kb_dataobject.list_of_dframes:
        filename = f"kb{kb_dataobject.id}_{kb_dataobject.fmt_product}_table{table_id}_release_as-{record_type}.json"
        # Try to make the build number the index
        if "Build Number" in dataframe.columns:
            # Make the build number the index of the data frame, so that it comes a json key
            dataframe.drop_duplicates(subset="Build Number", keep=False, inplace=True)
            dataframe.reset_index(drop=True)
            dataframe.set_index("Build Number", inplace=True)
        dataframe.to_json(
            f"{outputdir}{os.sep}{filename}",
            indent=4, orient=record_type, date_format="iso"
        )
        table_id += 1
