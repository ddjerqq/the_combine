import time
import json
import requests
from headers import random_useragent

proxy = {"https": "http://metacircuits:dZwUllzyyZWL41U0@p.litespeed.cc:31112"}


class Item(object):
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes

    @property
    def score(self) -> int:
        rarity = 100.0
        for attr in self.attributes:
            if attr["name"] != "Attribute count":
                rarity *= float(attr["rarity"]) / 100

        return round(1 / rarity)

    @classmethod
    def from_json(cls, data):
        return cls(
            data["name"],
            data["attributes"]
        )

    def __str__(self):
        return f"{self.name:<17} {self.score}"


# we can get a list of collections from this URL
# https://howrare.is/api/v0.1/collections/
def get_scores_of_collection(collection_name: str) -> list[Item]:
    """
    Returns a list of Items from a collection \n
    :param collection_name: The name of the collection to get prices for. \n
    :return: A list of Items.
    """

    fail = False
    while 1:
        try:
            r = requests.get(
                f"https://howrare.is/api/v0.1/collections/{collection_name.lower()}",
                headers={"User-Agent": random_useragent()},
                proxies=proxy if not fail else None
            )
            try:
                items = [Item.from_json(i) for i in r.json()["result"]["data"]["items"]]
            except json.JSONDecodeError:
                time.sleep(1)
                fail = True
                continue
            items = sorted(items, key=lambda x: x.score, reverse=True)
            return items
        except ConnectionError or requests.exceptions.ProxyError:
            fail = True
            time.sleep(1)




if __name__ == "__main__":
    metamounts = get_scores_of_collection("MetaMounts")
    for item in metamounts:
        print(item)
