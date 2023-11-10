import logging
import os
import re
from typing import Any, ClassVar, Dict, List

import requests
from bs4 import BeautifulSoup
from difflib  import SequenceMatcher
from filing_scraper.s3_manager import S3Manager
from filing_scraper.sns_publisher import SNSPublisher

logging.basicConfig(level=logging.INFO)
# source dict object
news_source_dict = {
    "glancy": {
        "name": "Glancy Prongay & Murray LLP",
        "source": {
            "globe_wire": {
                "url": "https://www.globenewswire.com/en/search/organization/Glancy%2520Prongay%2520&%2520Murray%2520LLP?page=1&pageSize=50",
                "tag": "a",
                "tag_query": {"data-autid": "article-url"},
                "split_ops": [{"title_split": "Against ", "substr_index": -1}],
            },
            "pharmiweb": {
                "url": "https://www.pharmiweb.com/search/?query=Glancy+Prongay+%26+Murray+LLP&type=4",
                "tag": "a",
                "tag_query": {"href": re.compile("/press-release/*")},
                "split_ops": [
                    {"title_split": "Announces Investigation of ", "substr_index": -1},
                    {"title_split": "on Behalf of Investors", "substr_index": 0},
                    {"title_split": "Continues Investigation of ", "substr_index": -1},
                ],
            },
        },
    },
    "kirby": {
        "name": "Kirby McInerney LLP",
        "source": {
            "globe_wire": {
                "url": "https://www.globenewswire.com/search/keyword/Kirby%252520McInerney%252520LLP?pageSize=50",
                "tag": "a",
                "tag_query": {"data-autid": "article-url"},
                "split_ops": [
                    {"title_split": "on Behalf of ", "substr_index": -1},
                    {"title_split": " Investors", "substr_index": 0},
                    {"title_split": "Investors in ", "substr_index": 0},
                    {"title_split": "Against ", "substr_index": -1},
                ],
            },
            "pharmiweb": {
                "url": "https://www.pharmiweb.com/search/?query=Kirby+McInerney+LLP&type=4",
                "tag": "a",
                "tag_query": {"href": re.compile("/press-release/*")},
                "split_ops": [
                    {"title_split": "Announces Investigation of ", "substr_index": -1},
                    {"title_split": "on Behalf of ", "substr_index": -1},
                    {"title_split": "Continues Investigation of ", "substr_index": -1},
                    {"title_split": " Investors ", "substr_index": 0},
                    {"title_split": "Against ", "substr_index": -1},
                ],
            },
        },
    },
    "pomerantz": {
        "name": "Pomerantz LLP",
        "source": {
            "globe_wire": {
                "url": "https://www.globenewswire.com/search/keyword/Pomerantz%252520LLP?pageSize=50",
                "tag": "a",
                "tag_query": {"data-autid": "article-url"},
                "split_ops": [
                    {"title_split": "Investors of ", "substr_index": -1},
                    {"title_split": "Investment in ", "substr_index": -1},
                    {"title_split": " of Class Action Lawsuit", "substr_index": 0},
                ],
            }
        },
    },
    "robbins": {
        "name": "Robbins Geller Rudman & Dowd LLP",
        "source": {
            "globe_wire": {
                "url": "https://www.globenewswire.com/search/keyword/Robbins%252520Geller%252520Rudman%252520&%252520Dowd%252520LLP?pageSize=50",
                "tag": "a",
                "tag_query": {"data-autid": "article-url"},
                "split_ops": [
                    {"title_split": "Against ", "substr_index": -1},
                    {"title_split": " and Announces", "substr_index": 0},
                    {"title_split": "Announces ", "substr_index": -1},
                    {"title_split": "INVESTOR DEADLINE NEXT WEEK: ", "substr_index": -1},
                    {"title_split": " Investors with Substantial", "substr_index": 0},
                    {"title_split": "Investigation into ", "substr_index": -1},
                    {"title_split": "Announces that ", "substr_index": -1},
                    {"title_split": " and Encourages", "substr_index": 0},
                    {"title_split": "that ", "substr_index": -1},
                ],
            },
            "pharmiweb": {
                "url": "https://www.pharmiweb.com/search/?query=Robbins+Geller+Rudman+%26+Dowd+LLP&type=4",
                "tag": "a",
                "tag_query": {"href": re.compile("/press-release/*")},
                "split_ops": [
                    {"title_split": "Against ", "substr_index": -1},
                    {"title_split": " and Announces", "substr_index": 0},
                    {"title_split": " Investors with Substantial", "substr_index": 0},
                    {"title_split": "Announces that ", "substr_index": -1},
                ],
            },
        },
    },
    "faruqi": {
        "name": "Faruqi & Faruqi LLP",
        "source": {
            "globe_wire": {
                "url": "https://www.globenewswire.com/search/keyword/Faruqi%252520&%252520Faruqi%252520LLP?pageSize=50",
                "tag": "a",
                "tag_query": {"data-autid": "article-url"},
                "split_ops": [
                    {"title_split": "Who Suffered Losses In ", "substr_index": -1},
                    {"title_split": " To Contact Him", "substr_index": 0},
                    {"title_split": "Otherwise Acquired ", "substr_index": -1},
                    {"title_split": " Securities Persuant", "substr_index": 0},
                    {"title_split": " Securities Pursuant and/or", "substr_index": 0},
                    {"title_split": " DEADLINE ALERT:", "substr_index": 0},
                ],
            },
            "pharmiweb": {
                "url": "https://www.pharmiweb.com/search/?query=Faruqi+%26+Faruqi+LLP&type=4",
                "tag": "a",
                "tag_query": {"href": re.compile("/press-release/*")},
                "split_ops": [
                    {"title_split": "Against ", "substr_index": -1},
                    {"title_split": " and Announces", "substr_index": 0},
                    {"title_split": " Investors with Substantial", "substr_index": 0},
                    {"title_split": "Announces that ", "substr_index": -1},
                ],
            },
        },
    },
    "levi": {
        "name": "Levi & Korinsky LLP",
        "source": {
            "globe_wire": {
                "url": "https://www.globenewswire.com/search/keyword/Levi%252520&%252520Korsinsky%CE%B4%252520LLP?pageSize=50",
                "tag": "a",
                "tag_query": {"data-autid": "article-url"},
                "split_ops": [
                    {"title_split": "Investors of a", "substr_index": 0},
                    {"title_split": "Notifies ", "substr_index": -1},
                    {"title_split": "by Officers of ", "substr_index": -1},
                ],
            }
        },
    },
}


class FilingScraper:
    _MATCH_THRESHOLD = 0.8
    _BANNED_WORDS: ClassVar = ["Press Releases", "\n", "\r\n", "\t", "Reminds", "Certified By", "INVESTOR ALERT"]

    def __init__(self, key: str, name:str, source: Dict) -> None:
        self.key = key
        self.name = name
        self.source_dict = source
        self.s3_manager = S3Manager()
        self.sns_publisher = SNSPublisher()
        curr_file = self.s3_manager.get_current_file(f"{self.key}.txt")
        self.unique_targets = self.populate_active_entries(curr_file)
        logging.info(f"ACTIVE UNIQUE TARGETS {self.unique_targets}")
    
    @property
    def email_header(self) -> str:
        return f"{self.name} New Filings"

    def exec_scraper(self):
        for source in self.source_dict.keys():
            logging.info(f"##### SEARCHING {source.upper()} ##### ")
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
            logging.warning(f"Could not reach {source_dict['url']}")
        # Initialize the object with the document
        soup = BeautifulSoup(res.content, "html.parser")
        target_tags = soup.findAll(source_dict["tag"], source_dict["tag_query"])
        new_targets = []
        for tag in target_tags:
            company = self.exec_split_ops(source_dict["split_ops"], tag.text)
            if self.is_unique(company):
                logging.info(company)
                new_targets.append(company.strip())
                self.unique_targets.append(company)
        if len(new_targets) > 0:
            self.sns_publisher.publish_email(subject=self.email_header,
                                             message=",\n".join(new_targets))
        self.s3_manager.update_file(self.unique_targets, f"{self.key}.txt")


def main(event, context) -> dict[str, Any]:
    logging.info("Running Scraping Event")
    for key in news_source_dict.keys():
        company_dict = news_source_dict[key]
        logging.info(f"{company_dict['name']}")
        scraper = FilingScraper(key, company_dict['name'], company_dict["source"])
        scraper.exec_scraper()
    response = {"success": True}
    return response

# if __name__ == "__main__":
#     logging.info("Running Scraping Event")
#     for key in news_source_dict.keys():
#         company_dict = news_source_dict[key]
#         logging.info(f"{company_dict['name']}")
#         scraper = FilingScraper(key, company_dict['name'], company_dict["source"])
#         scraper.exec_scraper()