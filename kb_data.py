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

    def get_resolution_section(self):
        """Extracts the resolution section from the KB article content section"""
        # Get the Section within the webpage that holds the desired data (make it a bit more targeted)
        return self.raw_html_article["content"][1]["Resolution"]

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
        # Since the HTML table has no header, we need to reassign the first row as heading
        for table_id in range(len(df)):
            df_header = df[table_id][:1]
            current_df = df[table_id][1:]
            current_df.columns = df_header.values.tolist()[0]
            # Get the data types right, especially the date format='%m/%d/%Y'
            releaseinfo_dataframe = current_df
            if "Release Date" in current_df.columns:
                releaseinfo_dataframe["Release Date"] = pd.to_datetime(current_df["Release Date"],
                                                                       infer_datetime_format=True, errors='coerce')
            # Skipping build number conversion. This produces non-deterministic results atm
            # if "Build Number" in current_df.columns:
            #     releaseinfo_dataframe["Build Number"] = pd.to_numeric(current_df["Build Number"],
            #                                                           errors='coerce', downcast="integer")
            list_of_release_df.append(releaseinfo_dataframe)
            # Fun stuff may happen with dataframes if not erased before the next iteration
            del df_header, current_df, releaseinfo_dataframe
        return list_of_release_df
