import json
import logging

import requests

from .datamodel import Contact

CONTACT_CACHE = {"timestamp": None, "contacts": []}


class ContactsClient:
    def __init__(self, baseUrl, authHeader):
        self.baseUrl = baseUrl
        self.authHeader = authHeader

    def getAll(self, **params):
        url = f"{self.baseUrl}/contacts"

        resp = requests.get(url, params=params,
                            headers=self.authHeader)
        try:
            data = json.loads(resp.content)
            contacts = data["contacts"]
            print(f"Contacts: {contacts}")

            return [Contact(**c).toJsonDict() for c in contacts]
        except TypeError as te:
            logging.exception("Error while decoding:", te)
            return []
