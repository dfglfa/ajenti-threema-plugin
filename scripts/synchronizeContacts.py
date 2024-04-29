import os
import sys
import datetime
import argparse

parser = argparse.ArgumentParser(description='Script for cron to update threema contacts')
parser.add_argument('--persist', action='store_true', help='Set this flag in order to persist the contact changes.')
args = parser.parse_args()
persist_changes = args.persist
log_prefix = "PERSISTENT" if persist_changes else "DRY-RUN"
print(f"***** Starting in {log_prefix} mode *****")

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
            f"{log_prefix}: Updating threemaId {threemaId} to {firstname} {lastname}, enabled: {enabled}")
        if persist_changes:
            client.applyContactChange(threemaId, firstname, lastname, enabled)

missing = changes.get("missing", [])
if missing:
    print(f"\n*** Found {len(missing)} missing contacts")
    for m in missing:
        threemaId = m.get("threemaId")
        firstName = m.get("firstName")
        lastName = m.get("lastName")
        print(
            f"{log_prefix}: Creating contact for threemaId {threemaId} with firstname {firstName} and lastname {lastName}")
        if persist_changes:
            client.createContact(threemaId, firstName, lastName)

if not missing and not updates:
    print("Everything in sync, nothing to do here.")
