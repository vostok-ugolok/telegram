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

    def assoc_add(self, order: dict, id: str):
        if self.data.get(order['order_id']) != None:
            self.data[order["order_id"]].append(id)
            self.data[order['order_id']] = list(set(self.data[order['order_id']]))
        else:
            self.data[order["order_id"]] = [id]