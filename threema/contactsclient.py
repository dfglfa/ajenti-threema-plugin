import io
import json
import logging
import time
import csv

import requests

CONTACTS_CACHE = {"timestamp": None, "contacts": []}


class ContactsClient:
    def __init__(self, baseUrl, authHeader):
        self.baseUrl = baseUrl
        self.authHeader = authHeader

    def getAll(self):
        now = int(time.time())
        if not CONTACTS_CACHE["timestamp"] or now - CONTACTS_CACHE["timestamp"] > 60:
            url = f"{self.baseUrl}/contacts"

            resp = requests.get(url, params={"pageSize": 2000},
                                headers=self.authHeader)
            data = json.loads(resp.content)
            contacts = data["contacts"]

            contacts = [c for c in contacts if not c["id"].startswith("*")]

            CONTACTS_CACHE["contacts"] = contacts
            CONTACTS_CACHE["timestamp"] = now

        return CONTACTS_CACHE["contacts"]

    def getEnabled(self):
        return [c for c in self.getAll() if c["enabled"]]

    def getContactsForUserIds(self, userIds):
        return [c for c in self.getAll() if c["id"] in userIds]

    def createContact(self, threemaId, firstname, lastname):
        url = f"{self.baseUrl}/contacts"

        logging.info(
            f"Creating contact for user {threemaId} with firstname '{firstname}' and lastname '{lastname}'")
        resp = requests.post(url,
                             json={"threemaId": threemaId,
                                   "firstName": firstname,
                                   "lastName": lastname,
                                   "enabled": True},
                             headers=self.authHeader)

        if resp.status_code <= 400:
            # avoid caching
            CONTACTS_CACHE["timestamp"] = None
            return "ok"
        else:
            logging.error(f"Could not create contact: {resp.content}")
            return "error"

    def updateContact(self, threemaId, firstname, lastname, enabled):
        url = f"{self.baseUrl}/contacts/{threemaId}"

        logging.info(
            f"Updating user {threemaId} to firstname '{firstname}' and lastname '{lastname}', ENABLED: {enabled}")
        resp = requests.put(url,
                            json={"firstName": firstname,
                                  "lastName": lastname,
                                  "enabled": enabled},
                            headers=self.authHeader)

        if resp.status_code <= 400:
            # avoid caching
            CONTACTS_CACHE["timestamp"] = None
            return "ok"
        else:
            logging.error(f"Could not update contact: {resp.content}")
            return "error"

    def deleteContact(self, threemaId):
        """
        This does NOT work for automatically created contacts :-/
        """
        url = f"{self.baseUrl}/contacts/{threemaId}"

        resp = requests.delete(url, headers=self.authHeader)

        if resp.status_code <= 400:
            CONTACTS_CACHE["timestamp"] = None
            logging.info(f"Contact successfully deleted {resp.content}")
            return "ok"
        else:
            logging.error(f"Contact not deleted: {resp.content}")
            return "error"

    def searchMembersByCsvFile(self, csvData, entUsers, threemaUsers):
        members, notFound = [], []
        try:
            reader = csv.DictReader(io.StringIO(csvData))
            for line in reader:
                firstname, lastname, classe = line["Prenom"], line["Nom"], line["Classe"]
                print(f"Checking {firstname} {lastname} from class {classe}")

                for entUser in entUsers:
                    if (entUser["givenName"], entUser["sn"], entUser["cls"]) == (firstname, lastname, classe):
                        print(
                            f"Found match for normalized name {entUser['normalizedName']}")

                        for tu in threemaUsers:
                            if tu["credentials_id"] == entUser['normalizedName']:
                                print(f"Found user id, too: {tu['id']}")
                                break

        except Exception as ex:
            logging.error(f"Cannot parse csv file: {ex}")

        return members, notFound
