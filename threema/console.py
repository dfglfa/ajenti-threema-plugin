
import random
from .threemaapi import ThreemaAdminClient


client = ThreemaAdminClient()
print("\n\n*** Threema admin interface (crappy console version) ***")

while True:
    print("\nNext action:")
    print("[ul]: List users")
    print("[ur]: Revoke user")
    print("[cl]: List all credentials")
    print("[cc]: Create credentials")
    print("[cu]: Update credentials")
    print("[cns]: Credentials naming scheme check")
    print("[cnc]: Credentials naming scheme correction")
    print("[ccc]: Check class assignment for all credentials")
    print("[q]: Quit")

    action = input("\nYour choice: ")

    if action == "ul":
        print("*** ALL USERS ***")
        users = client.getAllUsers(pageSize=0, page=0)
        print(f"Found {len(users)} users.")
        print('\n'.join(str(u) for u in users))
    elif action == "ur":
        print("*** REVOKE USER ***")
        print("Not implemented yet")
    elif action == "cl":
        print("*** ALL CREDENTIALS ***")
        creds = client.getAllCredentials(pageSize=0, page=0)
        print(f"Found {len(creds)} credentials")
        print('\n'.join(str(c) for c in creds))
    elif action == "cc":
        print("*** CREATE CREDENTIALS ***")
        username = input("Pick a username (default: random):")
        password = input("Pick a password (default: 'xxx1234567890'):")
        newCreds = client.createCredentials(
            username=(username or "user" +
                      str(random.randrange(1000, 10000))),
            password=(password or "xxx1234567890"))
    elif action == "cu":
        print("*** UPDATE CREDENTIALS ***")
        threemaId = input("Threema ID:")

        existingUser = client.getCredentialsDetails(threemaId)
        if not existingUser:
            print("User not found")
        else:
            username = input(
                f"New username (default: {existingUser.username}):")
            password = input("password (blank for no change):")

            client.updateCredentials(
                threemaId,
                username or existingUser.username,
                password or existingUser.password
            )
    elif action == "cns":
        print("*** CREDENTIALS NAMING SCHEME CHECK ***")
        res = client.checkCredentialsNamingScheme()
        print("Credentials OK: ", res["ok"])
        print("Credentials not OK: ", [r[1] for r in res["not_ok"]])
    elif action == "ccc":
        print("*** CLASS ASSIGNMENT CHECK ***")
        res = client.checkClassPrefixForAllStudents()

        allCreds = client.getAllCredentials(pageSize=0, page=0)
        password_dict = {c.id: c.password for c in allCreds}

        print(
            f"Found {len(res['ok'])} usernames that are already ok:\n", "\n".join(r[1] for r in res["ok"]), sep="")
        print(
            f"\nFound {len(res['unmatched'])} usernames that could not be matched:\n", "\n".join(r[1] for r in res["unmatched"]), sep="")
        print(
            f"\nFound {len(res['unused'])} names in my database that seem to have no threema account yet:\n", "\n".join(r for r in res["unused"]), sep="")
        print(
            f"\nFor the remaining {len(res['suggestions'])} users I have change suggestions:", res["suggestions"], sep="")
    elif action == "cnc":
        print("*** CREDENTIALS NAMING SCHEME CORRECTION ***")
        res = client.correctCredentialsNamingScheme()
        allCreds = client.getAllCredentials(pageSize=0, page=0)
        password_dict = {c.id: c.password for c in allCreds}

        print(f"\nNo fixes found for credentials:\n{res['notFixable']}")
        if not res["suggestions"]:
            print("No suggestions for correction found.")
            continue

        # contains tuple keys, e.g. ('6hJIVYCSvYlgwBpUAFyONw==', 'MaierTrezJu')
        # Values are change suggestions as list, e.g. ['7b_MaierTrezegueJulia', 'TES_MaierTrezegueJulien']
        comboKey_to_change_suggestions = res["suggestions"]

        # Maps int indexes to the above tuple keys
        indexed_suggestion_keys = {idx: suggestion_key for idx,
                                   suggestion_key in enumerate(comboKey_to_change_suggestions.keys())}

        print("\nSuggestions for correction:")
        for idx, suggestion_key in indexed_suggestion_keys.items():
            suggestions = comboKey_to_change_suggestions[suggestion_key]
            _, username = suggestion_key
            print(f"[{idx}] {username} => {suggestions}")

        print("\nWhich suggestions shall be applied?")
        print(
            "Enter indexes as comma-separated list or type 'ALL' to apply the first entry of all suggestions.")
        print(
            "For multiple suggestions use a secondary index, e.g. 12:1 to pick the second suggestion for entry 12.")
        print("Default is 0, i.e. the first index.")
        accepted_suggestions = input("\nYour choice ('x' to abort):")
        if accepted_suggestions == "x":
            pass
        elif accepted_suggestions == "ALL":
            print("Not implemented yet. Too insecure. :)")
        else:
            try:
                acceptedIndexes = [acc.strip()
                                   for acc in accepted_suggestions.split(",")]
                print("Applying suggestions", acceptedIndexes)

                for idx in acceptedIndexes:
                    parts = idx.split(":")
                    sugg_idx = int(parts[0])
                    sugg_list_idx = int(parts[1]) if len(parts) == 2 else 0

                    comboKey = indexed_suggestion_keys.get(sugg_idx)
                    suggestions_for_combo_key = comboKey_to_change_suggestions.get(
                        comboKey)
                    threemaId, _ = comboKey

                    try:
                        pickedNewUsername = suggestions_for_combo_key[sugg_list_idx]
                        client.updateCredentials(
                            threemaId, pickedNewUsername, password_dict.get(threemaId))
                    except Exception as ex:
                        print(f"Could not update threema id {threemaId}: {ex}")

            except Exception as ex:
                print("There was an error in your input", ex)

    elif action == "q":
        print("Bye\n")
        break
    else:
        print("Unknown command")
