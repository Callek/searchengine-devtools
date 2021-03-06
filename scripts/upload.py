#!/bin/python

import json
import requests
import sys

API_ENDPOINT = \
 "https://settings-writer.stage.mozaws.net/v1/" + \
 "buckets/main-workspace/collections/search-config/records"
# API_ENDPOINT = \
#  "https://settings-writer.prod.mozaws.net/v1/" + \
#  "buckets/main-workspace/collections/search-config/records"

# Fill this in!
AUTH = ""

with open('services/settings/dumps/main/search-config.json', 'r') as jsonFile:
    data = jsonFile.read()

engines = json.loads(data)

response = requests.get(API_ENDPOINT, headers={"Authorization": AUTH})

existingEngines = response.json()

# Handle python 2 backwards compatibility.
if sys.version_info[0] < 3:
    inputFn = raw_input
else:
    inputFn = input


def findEngine(id, engineSet):
    for engine in engineSet["data"]:
        if engine["webExtension"]["id"] == id:
            return engine
    return


def yes_or_no(question):
    while "the answer is invalid":
        reply = str(raw_input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False


for engine in engines["data"]:
    print(engine["webExtension"]["id"])

    existing = findEngine(engine["webExtension"]["id"], existingEngines)

    if not existing:
        response = requests.post(API_ENDPOINT, headers={"Authorization": AUTH},
                                 json={"data": engine})
        if response.status_code != 200 and response.status_code != 201:
            print("BAD UPLOAD!")
            print(response)
            print(response.status_code)
            print(response.text)
        continue

    # Delete things we don't want to upload / don't want to compare.
    existingId = existing["id"]
    for item in ["id", "last_modified", "schema"]:
        if item in engine:
            del engine[item]
        del existing[item]

    if engine == existing:
        print("Up to date")
        continue

    if yes_or_no('Upload changes to ' + engine["webExtension"]["id"]):
        response = requests.put(API_ENDPOINT + "/" + existingId,
                                headers={"Authorization": AUTH},
                                json={"data": engine})

        print(response.status_code)
        if response.status_code != 200 and response.status_code != 201:
            print("BAD UPDATE!")
            print(response.text)

enginesToRemove = []
for engine in existingEngines["data"]:
    newConfigEngine = findEngine(engine["webExtension"]["id"],
                                 engines)

    if not newConfigEngine:
        enginesToRemove.append(engine)

if len(enginesToRemove) > 0:
    print("\nEngines to Remove:\n")

    for engine in enginesToRemove:
        print engine["webExtension"]["id"]

    if yes_or_no('Are you sure you wish to remove the above engines?'):
        for engine in enginesToRemove:
            print engine["webExtension"]["id"]
            response = requests.delete(API_ENDPOINT + "/" + engine["id"],
                                       headers={"Authorization": AUTH})
            print(response.status_code)
            if response.status_code != 200 and response.status_code != 201:
                print("BAD DELETE!")
                print(response.text)
