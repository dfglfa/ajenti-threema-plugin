import os
import sys
import argparse
import datetime

parser = argparse.ArgumentParser(description='Script for cron to update threema groups')
parser.add_argument('--persist', action='store_true', help='Set this flag in order to persist the group changes.')
args = parser.parse_args()
persist_changes = args.persist
log_prefix = "PERSISTENT" if persist_changes else "DRY-RUN"
reference_time = datetime.datetime.now().isoformat()
print(f"\n***** Starting sync in {log_prefix} mode at {reference_time} *****\n")

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
sys.path.append(parent_dir)

from threema.config_loader import getThreemaTeacherGroupIds
from threema.threemaapi import ThreemaAdminClient
from threema.userdataprovider import LDAPUserDataProvider
from threema.utils import STANDARD_THREEMA_PREFIX

client = ThreemaAdminClient()
TEACHER_GROUP_IDS = getThreemaTeacherGroupIds()
ALL_CREDENTIALS = client.getAllCredentialsAsDict()

ALL_LDAP_USERS = LDAPUserDataProvider().getUserData()
ALL_THREEMA_USERS = client.getAllUsers()
ALL_TEACHERS = dict([(key, val) for key, val in ALL_LDAP_USERS.items() if val.get("cls") == "teachers"])
print(f"Found {len(ALL_TEACHERS)} teachers among {len(ALL_LDAP_USERS)} LDAP users.")

print("\n\n\n***** Building dictionary from LDAP Login names to active threema user ids.")
threemaUserIdForLDAPLogin = {}
isNewUser = {}
for ldapLogin in ALL_TEACHERS:
    credsName = f"{STANDARD_THREEMA_PREFIX}_{ldapLogin}"
    if credsName in ALL_CREDENTIALS:
        credsId = ALL_CREDENTIALS.get(credsName).id
        
        lastLoginDate = None
        for u in ALL_THREEMA_USERS:
            if u.get("credentials_id") == credsId:
                if lastLoginDate:
                    print(f"Found conflicting user with last login date {u.get('lastCheck')}, current value is {lastLoginDate}")
                    if lastLoginDate > u.get('lastCheck'):
                        print("IGNORING user because of older last login date.")
                        continue
                    else:
                        print(f"Overriding entry for {ldapLogin} with user Id {u.get('id')}")
                    
                threemaId = u.get("id")
                threemaUserIdForLDAPLogin[ldapLogin] = threemaId
                isNewUser[threemaId] = u.get("createdAt") > reference_time
                
                print(f"Found user ID {u.get('id')} for ldap login {ldapLogin}, created at {u.get('createdAt')}. New user? {isNewUser[threemaId]}")
                lastLoginDate = u.get("lastCheck")                
        
        if not threemaUserIdForLDAPLogin.get(ldapLogin):
            print(f"No active threema user yet for LDAP login {ldapLogin}")
    else:
        print(f"WARNING: LDAP user {ldapLogin} has no threema credentials yet!")

teacher_threema_user_ids = set(threemaUserIdForLDAPLogin.values())
print("\n\n\n***** STARTING GROUP SYNCHRONIZATION *****\n")

for teacher_group_id in TEACHER_GROUP_IDS:
    group_name = client.getGroupDetails(teacher_group_id).get("name")
    
    if not group_name:
        print(f"ERROR: Group ID {teacher_group_id} not found, please check entry in threema.yml")
        continue
    
    print(f"Synchronizing group with ID {teacher_group_id}. Group name is: '{group_name}'")
    members = client.getGroupMembers(teacher_group_id)
    member_id_list = [m['id'] for m in members]
    print(f"There are currently {len(member_id_list)} members in this group: {member_id_list}")
    
    remove_members = []
    for mid in member_id_list:
        if mid not in teacher_threema_user_ids:
            remove_members.append(mid)
            
    new_members = []
    for tid in teacher_threema_user_ids:
        if tid not in member_id_list:
            # activate later ...
            # if isNewUser[tid]:
            #    new_members.append(tid)
            #else:
            #    print(f"Missing user with ID {tid} will not be added to group {group_name}. Not a new user.")
            new_members.append(tid)
        
    print(f"{log_prefix} The following members are ADDED to this group: {new_members}")
    print(f"{log_prefix} The following members are REMOVED from this group: {remove_members}")    
    
    if persist_changes:
        needs_refresh = False
        if new_members:
            try:
                client.addGroupMembers(groupId=teacher_group_id, members=new_members)
                needs_refresh = True
            except Exception as ex:
                print("ERROR while adding new members: ", ex)
            
        if remove_members:
            try:
                client.removeGroupMembers(groupId=teacher_group_id, memberIds=remove_members)
                needs_refresh = True
            except Exception as ex:
                print("ERROR while removing obsolete members: ", ex)
        
        if needs_refresh:
            # Fake refresh. Necessary because groups are not synced on the users' devices 
            # after members are added or removed. :(
            dummy_group_name = group_name.strip() if group_name.endswith(" ") else group_name + " "
            print(f"Faking a group settings update, new group name is now '{dummy_group_name}' instead of '{group_name}'")
            client.updateGroup(teacher_group_id, dummy_group_name, saveChatHistory=False)
        
