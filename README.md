# Transform VMware product builds

This Python code parses VMware product release data from the kb article [Correlating build numbers and versions of VMware products (1014508)](https://kb.vmware.com/s/article/1014508?lang=en_US) 
and transforms them into a machine-readable format.  
A combination of parsing with [beautiful soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) and data handling with [Pandas](https://pandas.pydata.org/) is the used to achieve the goal.
A process is scheduled with GitHub actions to run daily, the results will be pushed to the repo [Machine-readable VMware release data](https://github.com/dominikzorgnotti/vmware_product_releases_machine-readable).

## Data standardization
Since v0.1.0 the raw data from the published KB is transformed to establish a standard in terms of column headers, formatting, etc.
KB 2143832 (ESXi) is used as the model for providing a standardized information set.

### Uniform column names
Columns describing the same data set have different labels, e.g. "Build number", "Build Number", "BuildNumber".  
In case of the example, the columns will be renamed to "Build Number" per KB 2143832.

### Multi-value columns
Columns may have more than one value, e.g. "Build Number - Version" in KB2143850 (vRealize Automation).  
In this case, two additional columns (Version, Build Number) will be added to the table each containing just a single Value.

### Merged tables
Roadmap: There may be more than one table that hold the version information, e.g. in KB2143838 (vCenter Server).
A merge operation will attempt to provide a unified table.

### Nested tables, merged columns/rows
Roadmap: Tables may have nested tables (e.g. KB52520 - VCF)
A decomposition is needed to provide the information in a usable format. 

## Output format and folder structures
The way the output is currently structured is:   
- Directory: based on Pandas options to handle [json data orientation](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html)
    - Files: KB(a)_(b)_table(c)_release_as_(d)"
       - a: knowledge base article id - the unique ID for the KB article
       - b: product name - The first product from the meta data, all in lower case and spaces replaced by underscores
       - c: An id to identify multiple html tables on the section (starting at 0)
       - d: json data orientation - see above

## Disclaimer

This is not an official VMware repository and in no way linked in official capacity to my employment at VMware.
