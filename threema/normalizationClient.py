
import logging
from .contactsclient import ContactsClient
from .credentialsclient import CredentialsClient
from .userclient import UserClient
from .userdataprovider import UserDataProvider


class NormalizationClient():
    def __init__(self, credentialsClient: CredentialsClient, userClient: UserClient, contactsClient: ContactsClient):
        self.credentialsClient = credentialsClient
        self.userClient = userClient
        self.contactsClient = contactsClient
        self.userDataProvider = UserDataProvider()

    def findNormalizations(self):
        entData = self.userDataProvider.getUserData()
        credentials = self.credentialsClient.getAll()
        users = self.userClient.getAll()
        contacts = self.contactsClient.getAll()

        normalized_name_to_common_name = {e["normalizedName"]: (
            e["givenName"], e["sn"], e["cls"]) for e in entData}

        cred_id_to_data = {c.id: c.username for c in credentials}
        cred_id_to_user = {u["credentials_id"]: u for u in users}
        user_id_to_contact = {c.id: c for c in contacts}

        for cred_id, cred_name in cred_id_to_data.items():
            if cred_name not in normalized_name_to_common_name:
                logging.info(
                    f"Cannot find ENT real name for credentials name {cred_name}")
                continue

            firstName, lastName, cls = normalized_name_to_common_name[cred_name]
            expected_nickname = f"{firstName} {lastName} {cls}"

            if cred_id not in cred_id_to_user:
                logging.info(f"Cannot find user for credentials {cred_name}")
                continue

            user = cred_id_to_user[cred_id]

            if user["nickname"] != expected_nickname:
                logging.info(
                    f"Deviation for user nickname {user['nickname']}, expected {expected_nickname}")

            if user["id"] not in user_id_to_contact:
                logging.info(f"No contact found for user id {user['id']}")
                continue

            contact = user_id_to_contact[user["id"]]
            expected_contact_firstname = f"{cls} {firstName}"
            if contact.firstName != expected_contact_firstname:
                logging.info(
                    f"Deviation for contact firstname {contact.firstName}, expected {expected_contact_firstname}")

            if contact.lastName != lastName:
                logging.info(
                    f"Deviation for contact lastname {contact.lastName}, expected {lastName}")
