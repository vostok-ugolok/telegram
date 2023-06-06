import os
import json

class Associations:
    def __init__(self):
        self.path = 'associations.json'
        self.data = {}
        if not os.path.exists('associations.json'):
            self.save()
        else:
            self.load()

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data)

    def load(self):
        with open(self.path, 'r') as f:
            self.data = json.load(self.data)

    def assoc(self, order: int, id: str):
        self.data[order] = id