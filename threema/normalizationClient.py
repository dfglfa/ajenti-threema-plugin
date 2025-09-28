
import logging
from threema.contactsclient import ContactsClient
from threema.credentialsclient import CredentialsClient
from threema.userclient import UserClient
from threema.userdataprovider import LDAPUserDataProvider
from threema.utils import STANDARD_THREEMA_PREFIX

# A constant value used as name for missing credentials
# Do not change, as it is used in the frontend
ORPHANED = "ORPHANED"


class NormalizationClient():
    def __init__(self, credentialsClient: CredentialsClient, userClient: UserClient, contactsClient: ContactsClient, userDataProvider: LDAPUserDataProvider):
        self.credentialsClient = credentialsClient
        self.userClient = userClient
        self.contactsClient = contactsClient
        self.userDataProvider = userDataProvider

    def findNormalizations(self):
        credentials = self.credentialsClient.getAll()
        users = self.userClient.getAll()
        contacts = self.contactsClient.getAll()
        entData = self.userDataProvider.getUserData()

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
                # Data not normed or enablement incorrect => include in update list
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
