import json
import logging
import time

import requests

from .datamodel import Contact

CONTACTS_CACHE = {"timestamp": None, "contacts": []}


class ContactsClient:
    def __init__(self, baseUrl, authHeader):
        self.baseUrl = baseUrl
        self.authHeader = authHeader

    def getAll(self):
        now = int(time.time())
        if not CONTACTS_CACHE["timestamp"] or now - CONTACTS_CACHE["timestamp"] > 60:
            url = f"{self.baseUrl}/contacts"

            params = {"pageSize": 2000}

            resp = requests.get(url, params=params,
                                headers=self.authHeader)
            try:
                data = json.loads(resp.content)
                contacts = data["contacts"]
                print(f"Contacts: {contacts}")

                contacts = [Contact(**c).toJsonDict() for c in contacts]
            except TypeError as te:
                logging.exception("Error while decoding:", te)
                contacts = []

            logging.info(f"**** Found {len(contacts)} contacts")
            CONTACTS_CACHE["contacts"] = contacts
            CONTACTS_CACHE["timestamp"] = now
        return CONTACTS_CACHE["contacts"]
