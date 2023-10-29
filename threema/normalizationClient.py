
import logging
from threema.contactsclient import ContactsClient
from threema.credentialsclient import CredentialsClient
from threema.userclient import UserClient
from threema.userdataprovider import UserDataProvider

# A constant value used as name for missing credentials
# Do not change, as it is used in the frontend
ORPHANED = "ORPHANED"


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
            e["givenName"], e["originalLastname"], e["cls"]) for e in entData}

        cred_name_for_cred_id = {c.id: c.username for c in credentials}
        user_for_cred_id = {u["credentials_id"]: u for u in users}
        contact_for_user_id = {c["id"]: c for c in contacts}

        # List of updates that are returned, but not yet applied.
        updates = []

        # List of missing contacts that need to be created
        missing = []

        # Track user ids that have been found in order to disable the remaining ones.
        not_found_user_ids = set(map(lambda u: u["id"], users))

        for cred_id, cred_name in cred_name_for_cred_id.items():
            logging.info(f"Checking credentials name {cred_name}")
            if cred_name not in normalized_name_to_common_name:
                logging.info(
                    f"Cannot find ENT user entry for credentials name {cred_name}")
                continue

            firstName, originalLastName, cls = normalized_name_to_common_name[cred_name]

            if cred_id not in user_for_cred_id:
                logging.info(
                    f"No user found for credentials {cred_name} - skipping")
                continue

            user = user_for_cred_id[cred_id]
            if user["id"] in not_found_user_ids:
                not_found_user_ids.remove(user["id"])

            normalized_contact_firstname = f"{cls} {firstName}" if cls != "teachers" else firstName
            normalized_contact_lastname = originalLastName

            if user["id"] not in contact_for_user_id:
                logging.info(f"No contact found for user id {user['id']}")
                missing.append(
                    {"threemaId": user["id"], "firstName": normalized_contact_firstname, "lastName": normalized_contact_lastname})
                continue

            contact = contact_for_user_id[user["id"]]

            logging.info(
                f"Expecting first name name {normalized_contact_firstname} and last name {normalized_contact_lastname}")

            if contact["firstName"] != normalized_contact_firstname or contact["lastName"] != originalLastName or not contact["enabled"]:
                logging.info(
                    f"Deviation for contact {contact['firstName']} {contact['lastName']} ENABLED={contact['enabled']}, expected enabled contact {normalized_contact_firstname} {originalLastName}")
                updates.append({
                    "firstName": contact["firstName"],
                    "firstNameNormalized": normalized_contact_firstname,
                    "lastName": contact["lastName"],
                    "lastNameNormalized": originalLastName,
                    "threemaId": user["id"],
                    "credentialsName": cred_name,
                    "enabled": True
                })

        for upi in not_found_user_ids:
            con = contact_for_user_id.get(upi)
            if con and con["enabled"]:
                logging.warn(
                    f"DISABLING orphaned contact {con['firstName']} {con['lastName']} for user id {upi}")
                updates.append({
                    "firstName": con["firstName"],
                    "firstNameNormalized": con["firstName"],
                    "lastName": con["lastName"],
                    "lastNameNormalized": con["lastName"],
                    "threemaId": upi,
                    "credentialsName": ORPHANED,
                    "enabled": False
                })

        return {"updates": updates, "missing": missing}
