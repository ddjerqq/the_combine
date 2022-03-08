d = {
    "name": "Funny Bone #1",
    "description": "",
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




class Attribute:
    def __init__(self, t, v):
        self.type  = t
        self.value = v

    @classmethod
    def from_json(cls, data: dict):
        t = data["trait_type"]
        v = data["value"]
        return cls(t, v)

    def __str__(self):
        return f"{self.type}: {self.value}"



class Metadata:
    def __init__(self, name: str, description: str, image: str, attributes: list[Attribute]):
        self.name = name
        self.description = description
        self.image = image
        self.attributes = attributes

    @classmethod
    def from_json(cls, data: dict):
        name = data["name"]
        description = data["description"]
        image = data["image"]
        attributes = [Attribute.from_json(a) for a in data["attributes"]]
        return cls(name, description, image, attributes)

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}\n{self.description}\n{self.image}\n{self.attributes}"

