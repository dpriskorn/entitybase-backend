#!/usr/bin/env python3
from pprint import pprint

from pydantic import BaseModel
import json

class TestModel(BaseModel):
    mainsnak: str = "example_snak"
    qualifiers: dict = {"P123": [{"snaktype": "value", "property": "P123", "datavalue": {"type": "string", "value": "test"}}]}
    references: list = [{"snaks": {"P123": [{"snaktype": "value", "property": "P123", "datavalue": {"type": "string", "value": "ref"}}]}}]
    type: str = "statement"
    rank: str = "normal"

model = TestModel()
dump = model.model_dump(mode="json")
json_dump = model.model_dump_json()
print("Dict:")
pprint(dump)
print("pydantic Json dump:")
pprint(json.loads(json_dump))
print("len(json_dump):", len(json_dump))  # Number of keys
print("len(json.dumps(dump)):", len(json.dumps(dump)))  # JSON string length
print("JSON string length with sort_keys:", len(json.dumps(dump, sort_keys=True)))
print("JSON string length without spaces:", len(json.dumps(dump).replace(" ", "")))
