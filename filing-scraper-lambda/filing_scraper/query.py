from dataclasses import dataclass
from typing import List, Dict
import logging

@dataclass
class FilingSource():
    url: str
    tag: str
    tag_query: Dict
    split_ops: List[Dict]


class QueryFirm():
    def __init__(self, name: str) -> None:
        self.name = name
        self.source = {}
    
    @property
    def return_query(self):
        { self.name: self.source}
    
    def add_source(self, key: str, source: FilingSource) -> None:
        if key in source:
            logging.warning(f"Key {key} already exists")
        self.source[key] = source
    


def return_mock_source() -> FilingSource:
    return FilingSource(url="https://www.globenewswire.com/search/keyword/Pomerantz%252520LLP?pageSize=50",
                        tag="a",
                        tag_query={"data_autid": "article-url"},
                        split_ops=[{"title_split": "Investors of ", "substr_index": -1},
                                   {"title_split": "Investment in ", "substr_index": -1},
                                   {"title_split": " of Class Action Lawsuit", "substr_index": 0}])


def generate_mock_query_list() -> List[QueryFirm]:
    query = QueryFirm(name="mock_query")
    query.add_source(key="mock_source",
                     source=return_mock_source())
    return [query]