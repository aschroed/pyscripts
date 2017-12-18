#!/usr/bin/env python
import json

with open('/Users/andrew/Desktop/ontology.json') as ontf:
    data = json.load(ontf)

#sorted_data = {}
#for key in sorted(data):
#    sorted_data[key] = data[key

with open('/Users/andrew/Desktop/pretty_ontology.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)
