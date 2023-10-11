import json
import logging
import time

import requests

CONTACTS_CACHE = {"timestamp": None, "contacts": []}


class ContactsClient:
    def __init__(self, baseUrl, authHeader):
        self.baseUrl = baseUrl
        self.authHeader = authHeader

    def getAll(self, **params):
        now = int(time.time())
        if params or not CONTACTS_CACHE["timestamp"] or now - CONTACTS_CACHE["timestamp"] > 60:
            url = f"{self.baseUrl}/contacts"

            params["pageSize"] = 2000

            resp = requests.get(url, params=params,
                                headers=self.authHeader)
            data = json.loads(resp.content)
            contacts = data["contacts"]

            contacts = [c for c in contacts if c["enabled"]
                        and not c["id"].startswith("*")]

            if "filterIds" in params:
                logging.info(
                    f"Filtering contacts with ids {params['filterIds']}")
                return [c for c in contacts if c["id"]
                        in params["filterIds"]]

            CONTACTS_CACHE["contacts"] = contacts
            CONTACTS_CACHE["timestamp"] = now

        return CONTACTS_CACHE["contacts"]

    def updateContact(self, threemaId, firstname, lastname):
        url = f"{self.baseUrl}/contacts/{threemaId}"

        logging.info(
            f"Updating user {threemaId} to firstname '{firstname}' and lastname '{lastname}'")
        resp = requests.put(url,
                            json={"firstName": firstname,
                                  "lastName": lastname, "enabled": True},
                            headers=self.authHeader)

        if resp.status_code <= 400:
            # avoid caching
            CONTACTS_CACHE["timestamp"] = None
            return "ok"
        else:
            return "error"

    def deleteContact(self, threemaId):
        url = f"{self.baseUrl}/contacts/{threemaId}"

        logging.warn(
            f"Deleting contact for user {threemaId}")
        resp = requests.delete(url, headers=self.authHeader)

        if resp.status_code <= 400:
            CONTACTS_CACHE["timestamp"] = None
            return "ok"
        else:
            return "error"
