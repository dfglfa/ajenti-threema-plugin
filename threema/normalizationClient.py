
import logging
from threema.contactsclient import ContactsClient
from threema.credentialsclient import CredentialsClient
from threema.userclient import UserClient
from threema.entuserdataprovider import ENTUserDataProvider
from threema.utils import STANDARD_THREEMA_PREFIX

# A constant value used as name for missing credentials
# Do not change, as it is used in the frontend
ORPHANED = "ORPHANED"


class NormalizationClient():
    def __init__(self, credentialsClient: CredentialsClient, userClient: UserClient, contactsClient: ContactsClient, entUserDataProvider: ENTUserDataProvider):
        self.credentialsClient = credentialsClient
        self.userClient = userClient
        self.contactsClient = contactsClient
        self.entUserDataProvider = entUserDataProvider

    def findNormalizations(self):
        credentials = self.credentialsClient.getAll()
        users = self.userClient.getAll()
        contacts = self.contactsClient.getAll()
        entData = self.entUserDataProvider.getUserData()

        contact_for_user_id = {c["id"]: c for c in contacts}
        cred_name_for_cred_id = {c.id: c.username for c in credentials}

        # List of updates that are returned, but not yet applied.
        updates = []

        # List of missing contacts that need to be created
        missing = []

        # List of credentials names that have not been found in ENT
        no_ent_match = []

        # Track user ids that have been found in order to disable the remaining ones.
        not_found_user_ids = set(map(lambda u: u["id"], users))

        for u in users:

            # If a user is found, we assume an active user and thus do NOT disable a contact
            # for this user id.
            if u["id"] in not_found_user_ids:
                not_found_user_ids.remove(u["id"])

            cred_id = u["credentials_id"]
            cred_name = cred_name_for_cred_id.get(cred_id)

            if not cred_name:
                logging.info(f"IGNORING orphaned user {u['id']}")
                continue

            ent_login_for_cred = cred_name[len(STANDARD_THREEMA_PREFIX)+1:] if cred_name.startswith(STANDARD_THREEMA_PREFIX) else cred_name
            entUserData = entData.get(ent_login_for_cred)

            if not entUserData:
                logging.error(f"ENT user for creds name {cred_name} not found (tried to match {ent_login_for_cred})")
                no_ent_match.append({"threemaId": u["id"], "credentials_name": cred_name})
                continue
            
            normed_first_name = f"{entUserData['cls']} {entUserData['firstName'].split()[0]}" if entUserData['cls'] != "teachers" else entUserData['firstName']
            normed_last_name = entUserData['lastName']
            logging.info(f"Contact name of user {u['id']} should be {normed_first_name} {normed_last_name}")

            actual_contact = contact_for_user_id.get(u['id'])

            if not actual_contact:
                # Mark as missing in order to have the contact created
                logging.info(f"No contact yet for user {u['id']}")
                missing.append({"threemaId": u["id"], "firstName": normed_first_name, "lastName": normed_last_name})

            elif actual_contact["firstName"] != normed_first_name or actual_contact["lastName"] != normed_last_name or not actual_contact["enabled"]:
                # Data not normed of enablement incorrect => include in update list
                updates.append({"firstName": actual_contact["firstName"],
                    "firstNameNormalized": normed_first_name,
                    "lastName": actual_contact["lastName"],
                    "lastNameNormalized": normed_last_name,
                    "threemaId": u["id"],
                    "credentialsName": cred_name,
                    "enabled": True})
                
        # Last step: For each user ID that has not been found among the active users,
        # we look for an existing contact and disable it, if active. 
        # (Contacts cannot always be deleted, just disabled)
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

        return {"updates": updates, "missing": missing, "no_ent_match": no_ent_match}


    def _findNormalizations(self):
        entData = self.entUserDataProvider.getUserData()
        credentials = self.credentialsClient.getAll()
        users = self.userClient.getAll()
        contacts = self.contactsClient.getAll()

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
            if cred_name not in entData:
                logging.info(
                    f"Cannot find ENT user entry for credentials name {cred_name}")
                continue

            firstName, originalLastName, cls = (entData[cred_name]["firstName"],
                                                entData[cred_name]["lastName"],
                                                entData[cred_name]["cls"])

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
