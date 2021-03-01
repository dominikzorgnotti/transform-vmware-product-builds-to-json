import requests

# import beatufilsoup4

BASEURL_VMWARE_KB = "https://kb.vmware.com/services/apexrest/v1/article?docid="


def get_kb_webdata(kb_article_id: int):
    """Accepts an int with the KB article id and will return the wbe response as JSON output"""
    vmware_kb_url = f"{BASEURL_VMWARE_KB}{str(kb_article_id)}"
    response = requests.get(vmware_kb_url)
    response.raise_for_status()
    return response.json()


def parse_kb_article_ids(kb_article: int):
    """Accepts an int with the KB article id holding the sub-pages with the release data. Returns these as list of int"""
    # raw_json = get_kb_webdata(kb_article)
    # TODO do something meaningful here
    # TODO return list of int with all the KBs
    pass
