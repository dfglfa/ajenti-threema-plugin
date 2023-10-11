
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
        user_id_to_contact = {c["id"]: c for c in contacts}

        changes = []
        unprocessed_user_ids = set(map(lambda u: u["id"], users))

        for cred_id, cred_name in cred_id_to_data.items():
            logging.info(f"Checking credentials name {cred_name}")
            if cred_name not in normalized_name_to_common_name:
                logging.info(
                    f"Cannot find ENT real name for credentials name {cred_name}")
                continue

            firstName, lastName, cls = normalized_name_to_common_name[cred_name]

            if cred_id not in cred_id_to_user:
                logging.info(f"Cannot find user for credentials {cred_name}")
                continue

            user = cred_id_to_user[cred_id]

            if user["id"] not in user_id_to_contact:
                logging.info(f"No contact found for user id {user['id']}")
                continue

            if user["id"] in unprocessed_user_ids:
                unprocessed_user_ids.remove(user["id"])

            contact = user_id_to_contact[user["id"]]
            expected_contact_firstname = f"{cls} {firstName}" if cls != "teachers" else firstName

            logging.info(
                f"Expecting first name name {expected_contact_firstname} and last name {lastName}")

            if contact["firstName"] != expected_contact_firstname or contact["lastName"] != lastName:
                logging.info(
                    f"Deviation for contact {contact['firstName']} {contact['lastName']}, expected {expected_contact_firstname} {lastName}")
                change = {
                    "firstName": contact["firstName"],
                    "firstNameNormalized": expected_contact_firstname,
                    "lastName": contact["lastName"],
                    "lastNameNormalized": lastName,
                    "threemaId": user["id"],
                    "credentialsName": cred_name
                }
                changes.append(change)

        for upi in unprocessed_user_ids:
            con = user_id_to_contact.get(upi)
            if con:
                logging.warn(
                    f"DISABLING orphaned contact {con['firstName']} {con['lastName']} for user id {upi}")
                self.contactsClient.updateContact(
                    upi, con['firstName'], con['lastName'], False)

        return changes
