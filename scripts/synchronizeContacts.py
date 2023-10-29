import os
import sys

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
sys.path.append(parent_dir)

from threema.threemaapi import ThreemaAdminClient

client = ThreemaAdminClient()
changes = client.findNormalizations()

updates = changes.get("updates", [])
print(f"\n*** Found {len(updates)} updates\n")
for update in updates:
    threemaId = update.get("threemaId")
    firstname = update.get("firstNameNormalized")
    lastname = update.get("lastNameNormalized")
    enabled = update.get("enabled", True)
    print(
        f"Updating threemaId {threemaId} to {firstname} {lastname}, enabled: {enabled}")
    client.applyContactChange(threemaId, firstname, lastname, enabled)

missing = changes.get("missing", [])
print(f"\n*** Found {len(missing)} missing contacts\n")
for m in missing:
    threemaId = m.get("threemaId")
    firstName = m.get("firstName")
    lastName = m.get("lastName")
    print(
        f"Creating contact for threemaId {threemaId} with firstname {firstName} and lastname {lastName}")
    client.createContact(threemaId, firstName, lastName)
