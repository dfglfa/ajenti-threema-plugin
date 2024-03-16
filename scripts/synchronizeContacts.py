import os
import sys
import datetime

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
sys.path.append(parent_dir)

from threema.threemaapi import ThreemaAdminClient

client = ThreemaAdminClient()
changes = client.findNormalizations()

now = datetime.datetime.now()
updates = changes.get("updates", [])
print(f"\nSync running at {now.strftime('%d.%m.%y %H:%M')}")

if updates:
    print(f"*** Found {len(updates)} updates")
    for update in updates:
        threemaId = update.get("threemaId")
        firstname = update.get("firstNameNormalized")
        lastname = update.get("lastNameNormalized")
        enabled = update.get("enabled", True)
        print(
            f"Updating threemaId {threemaId} to {firstname} {lastname}, enabled: {enabled}")
        print("UPDATE CURRENTLY DISABLED")
        #client.applyContactChange(threemaId, firstname, lastname, enabled)

missing = changes.get("missing", [])
if missing:
    print(f"\n*** Found {len(missing)} missing contacts")
    for m in missing:
        threemaId = m.get("threemaId")
        firstName = m.get("firstName")
        lastName = m.get("lastName")
        print(
            f"Creating contact for threemaId {threemaId} with firstname {firstName} and lastname {lastName}")
        print("CREATION CURRENTLY DISABLED")
        #client.createContact(threemaId, firstName, lastName)

if not missing and not updates:
    print("Everything in sync, nothing to do here.")
