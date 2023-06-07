import os
import json

class Associations:
    def __init__(self):
        self.path = 'associations.json'
        self.data = dict()
        if not os.path.exists('associations.json'):
            self.save()
        else:
            self.load()

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f)

    def load(self):
        with open(self.path, 'r') as f:
            self.data = dict(json.load(f))

    def assoc(self, order: dict, id: str):
        self.data[order["order_id"]] = id