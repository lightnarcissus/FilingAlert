import logging
import os
import re
from typing import Any, ClassVar, Dict, List

import requests
from bs4 import BeautifulSoup
from difflib  import SequenceMatcher
from filing_scraper.s3_manager import S3Manager
from filing_scraper.query import generate_mock_query_list, QueryFirm
from filing_scraper.sns_publisher import SNSPublisher

logger = logging.getLogger()


class FilingScraper:
    _MATCH_THRESHOLD = 0.8
    _BANNED_WORDS: ClassVar = ["Press Releases", "\n", "\r\n", "\t", "Reminds", "Certified By", "INVESTOR ALERT"]

    def __init__(self, key: str, name:str, source: Dict) -> None:
        self.key = key
        self.name = name
        self.source_dict = source
        self.s3_manager = S3Manager()
        self.sns_publisher = SNSPublisher()
    
    def prep_data(self) -> None:
        curr_file = self.s3_manager.get_current_file(f"{self.key}.txt")
        self.unique_targets = self.populate_active_entries(curr_file)
    
    @property
    def email_header(self) -> str:
        return f"{self.name} New Filings"

    def exec_scraper(self):
        for source in self.source_dict.keys():
            print(f"##### SEARCHING {source.upper()} ##### ")
            self.return_unique_targets_for_source(self.source_dict[source])
            pass

    def populate_active_entries(self, file_path: str) -> List[str]:
        if not os.path.exists(file_path):
            raise FileNotFoundError("Could not find downloaded file")
        result = []
        with open(file_path) as entry_file:
            for line in entry_file.readlines():
                result.append(line)
        return result

    def is_unique(self, target) -> bool:
        if len(target) < 1 or any(
            ele.encode("utf-8") in target.encode("utf-8", "ignore") for ele in self._BANNED_WORDS
        ):
            return False
        for item in self.unique_targets:
            if SequenceMatcher(None, target, item).ratio() > self._MATCH_THRESHOLD:
                return False
        return True

    def exec_split_ops(self, split_ops: Dict, text: str) -> str:
        result = text
        for op in split_ops:
            result = result.split(op["title_split"])[int(op["substr_index"])]
        return result

    def return_unique_targets_for_source(self, source_dict: Dict) -> List:
        # getting response object
        try:
            res = requests.get(source_dict["url"], timeout=10)
        except requests.exceptions.Timeout:
            logger.warning(f"Could not reach {source_dict['url']}")
        # Initialize the object with the document
        soup = BeautifulSoup(res.content, "html.parser")
        target_tags = soup.findAll(source_dict["tag"], source_dict["tag_query"])
        new_targets = []
        for tag in target_tags:
            company = self.exec_split_ops(source_dict["split_ops"], tag.text)
            if self.is_unique(company):
                print(company)
                new_targets.append(company.strip())
                self.unique_targets.append(company)
        if len(new_targets) > 0:
            self.sns_publisher.publish_email(subject=self.email_header,
                                             message=",\n".join(new_targets))
        self.s3_manager.update_file(self.unique_targets, f"{self.key}.txt")


def main(event, context) -> dict[str, Any]:
    # replace with your own QueryFirm instances
    target_queries = generate_mock_query_list()
    for query in target_queries:
        firm_query = query.return_query()
        print(f"{firm_query.name}")
        scraper = FilingScraper(query, firm_query.name, firm_query.source)
        scraper.prep_data()
        scraper.exec_scraper()
    response = {"success": True}
    return response