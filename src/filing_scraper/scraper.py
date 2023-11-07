import requests
import re
from bs4 import BeautifulSoup
from typing import Dict, List
from difflib import SequenceMatcher

# source dict object
news_source_dict = {
    "glancy":{
        "name": "Glancy Prongay & Murray LLP",
        "source":{
            "globe_wire": { 
                "url" : 'https://www.globenewswire.com/en/search/organization/Glancy%2520Prongay%2520&%2520Murray%2520LLP?page=1&pageSize=50',
                "tag": 'a',
                "tag_query": {'data-autid': "article-url"},
                "split_ops":[{
                    "title_split": "Against ",
                    "substr_index": -1
                }]
            },
            "pharmiweb":{
                "url": 'https://www.pharmiweb.com/search/?query=Glancy+Prongay+%26+Murray+LLP&type=4',
                "tag": 'a',
                "tag_query": {'href': re.compile('/press-release/*')},
                "split_ops": [{
                    "title_split": "Announces Investigation of ",
                    "substr_index": -1
                },
                {
                    "title_split": "on Behalf of Investors",
                    "substr_index": 0
                },
                {
                    "title_split": "Continues Investigation of ",
                    "substr_index": -1
                }
                ]
            }
        }
    },
    "kirby":{
        "name": "Kirby McInerney LLP",
        "source":{
            "globe_wire": { 
                "url" : 'https://www.globenewswire.com/search/keyword/Kirby%252520McInerney%252520LLP?pageSize=50',
                "tag": 'a',
                "tag_query": {'data-autid': "article-url"},
                "split_ops":[
                {
                    "title_split": "on Behalf of ",
                    "substr_index": -1
                },
                {
                    "title_split": " Investors",
                    "substr_index": 0
                },
                {
                    "title_split": "Investors in ",
                    "substr_index": 0
                },
                {
                    "title_split": "Against ",
                    "substr_index": -1
                },
                ]
            },
            "pharmiweb":{
                "url": 'https://www.pharmiweb.com/search/?query=Kirby+McInerney+LLP&type=4',
                "tag": 'a',
                "tag_query": {'href': re.compile('/press-release/*')},
                "split_ops": [{
                    "title_split": "Announces Investigation of ",
                    "substr_index": -1
                },
                {
                    "title_split": "on Behalf of ",
                    "substr_index": -1
                },
                {
                    "title_split": "Continues Investigation of ",
                    "substr_index": -1
                },
                {
                    "title_split": " Investors ",
                    "substr_index": 0
                },
                {
                    "title_split": "Against ",
                    "substr_index": -1
                }
                ]
            }
        }
    },
    "pomerantz":{
        "name": "Pomerantz LLP",
        "source":{
            "globe_wire": { 
                "url" : 'https://www.globenewswire.com/search/keyword/Pomerantz%252520LLP?pageSize=50',
                "tag": 'a',
                "tag_query": {'data-autid': "article-url"},
                "split_ops":[
                {
                    "title_split": "Investors of ",
                    "substr_index": -1
                },
                {
                    "title_split": "Investment in ",
                    "substr_index": -1
                },
                {
                    "title_split": " of Class Action Lawsuit",
                    "substr_index": 0
                },
                ]
            }
        }
    },
    "robbins":{
        "name": "Robbins Geller Rudman & Dowd LLP",
        "source":{
            "globe_wire": { 
                "url" : 'https://www.globenewswire.com/search/keyword/Robbins%252520Geller%252520Rudman%252520&%252520Dowd%252520LLP?pageSize=50',
                "tag": 'a',
                "tag_query": {'data-autid': "article-url"},
                "split_ops":[
                {
                    "title_split": "Against ",
                    "substr_index": -1
                },
                {
                    "title_split": " and Announces",
                    "substr_index": 0
                },
                {
                    "title_split": "Announces ",
                    "substr_index": -1
                },
                {
                    "title_split": "INVESTOR DEADLINE NEXT WEEK: ",
                    "substr_index": -1
                },
                {
                    "title_split": " Investors with Substantial",
                    "substr_index": 0
                },
                {
                    "title_split": "Investigation into ",
                    "substr_index": -1
                },
                {
                    "title_split": "Announces that ",
                    "substr_index": -1
                },
                ]
            },
            "pharmiweb":{
                "url": 'https://www.pharmiweb.com/search/?query=Robbins+Geller+Rudman+%26+Dowd+LLP&type=4',
                "tag": 'a',
                "tag_query": {'href': re.compile('/press-release/*')},
                "split_ops": [   
                {
                    "title_split": "Against ",
                    "substr_index": -1
                },
                {
                    "title_split": " and Announces",
                    "substr_index": 0
                },
                {
                    "title_split": " Investors with Substantial",
                    "substr_index": 0
                },
                {
                    "title_split": "Announces that ",
                    "substr_index": -1
                },
                ]
            }
        }
    },
}
class FilingScraper():
    _BANNED_WORDS = ["Press Releases", "\r\n", "\t", "Investors", "Reminds", "INVESTOR ALERT"]
    def __init__(self, source: Dict) -> None:
        self.source_dict = source
        self.unique_targets = []
        pass

    def exec(self):
        for source in self.source_dict.keys():
            print(f"##### SEARCHING {source.upper()} ##### ")
            self.return_unique_targets_for_source(self.source_dict[source])
            pass


    def is_unique(self, target) -> bool:
        if len(target)< 1 or any(ele.encode('utf-8') in target.encode('utf-8', 'ignore') for ele in self._BANNED_WORDS):
            return False
        for item in self.unique_targets:
            if SequenceMatcher(None, target, item).ratio() > 0.8:
                return False
        return True

    def exec_split_ops(self, split_ops: Dict, text: str) -> str:
        result = text
        for op in split_ops:
            result = result.split(op['title_split'])[int(op['substr_index'])]
        return result

    def return_unique_targets_for_source(self, source_dict: Dict) -> List:
        # getting response object
        res = requests.get(source_dict['url'])

        # Initialize the object with the document
        soup = BeautifulSoup(res.content, "html.parser")
        target_tags = soup.findAll(source_dict['tag'], source_dict['tag_query'])

        for tag in target_tags:
            company = self.exec_split_ops(source_dict["split_ops"], tag.text)
            if self.is_unique(company):
                print(company)
                self.unique_targets.append(company)


if __name__=='__main__':
    for key in news_source_dict.keys():
        company_dict = news_source_dict[key]
        print(f"{company_dict['name']}")
        scraper = FilingScraper(company_dict["source"])
        scraper.exec()
