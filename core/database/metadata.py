from __future__ import annotations

__d = {
    "name": "Funny Bone #1",
    "description": "funn bone description",
    "image": "https://tastybones.mypinata.cloud/ipfs/QmZaJg6B5SQzVSuCXZrPTGSc9Cn3SmgUWdjehNis521QAG",
    "attributes":
        [
            {"trait_type": "Background", "value": "BPPY Gradient"},
            {"trait_type": "Body", "value": "White Polo w/ Red Necktie"},
            {"trait_type": "Type", "value": "Funny Bones"},
            {"trait_type": "Head", "value": "Toxic"},
            {"trait_type": "Headwear", "value": "Green-Purple Beanie"},
            {"trait_type": "Eyewear", "value": "Lightning Bolt"}
        ]
}



class Metadata:
    def __init__(self, name: str, attributes: list[tuple[str, str]]):
        self.name = name
        self.attributes = attributes

    @classmethod
    def from_json(cls, json_metada: dict):
        """
        Construct a Metadata object from json response. auto handles key
        :param json_metada:
        :return: Metadata object, with attributes sorted into a list of tuples
        """
        _k_name = "name"
        _k_type = "attribute_type"
        _k_val  = "attribute_value"
        _k_attr = "attributes"

        for key in json_metada.keys():
            if "name" in key:
                _k_name = key
            if "attribute" in key:
                _k_type = key

        attributes = json_metada[_k_attr]
        name = json_metada[_k_name]

        for key, val in attributes[0].items():
            if "name" in key:
                _k_name = key
            if "type" in key:
                _k_type = key
            if "value" in key:
                _k_val = key

        tuple_attributes = [(a[_k_type] or "null", a[_k_val] or "null") for a in attributes]

        return cls(name, tuple_attributes)

    @property
    def to_database(self):
        payload = []
        for attr in self.attributes:
            payload.append((self.name, attr[0], attr[1]))
        return payload

    def __str__(self):
        return f"{self.name}\n{self.attributes}"



if __name__ == "__main__":
    m = Metadata.from_json(__d)
    print(m)
