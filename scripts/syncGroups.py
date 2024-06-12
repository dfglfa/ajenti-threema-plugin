import os
import sys
import argparse

parser = argparse.ArgumentParser(description='Script for cron to update threema groups')
parser.add_argument('--persist', action='store_true', help='Set this flag in order to persist the group changes.')
args = parser.parse_args()
persist_changes = args.persist
log_prefix = "PERSISTENT" if persist_changes else "DRY-RUN"
print(f"***** Starting in {log_prefix} mode *****")

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
sys.path.append(parent_dir)

from threema.config_loader import getThreemaTeacherGroupIds
from threema.threemaapi import ThreemaAdminClient
from threema.entuserdataprovider import ENTUserDataProvider
from threema.utils import STANDARD_THREEMA_PREFIX

client = ThreemaAdminClient()
TEACHER_GROUP_IDS = getThreemaTeacherGroupIds()
ALL_CREDENTIALS = client.getAllCredentialsAsDict()

ALL_ENT_USERS = ENTUserDataProvider().getUserData()
ALL_THREEMA_USERS = client.getAllUsers()
ALL_TEACHERS = dict([(key, val) for key, val in ALL_ENT_USERS.items() if val.get("cls") == "teachers"])
print(f"Found {len(ALL_TEACHERS)} teachers among {len(ALL_ENT_USERS)} ENT users.")

print("\n\n\n***** Building dictionary from entLogin names to active threema user ids.")
threemaUserIdForENTLogin = {}
for entLogin in ALL_TEACHERS:
    credsName = f"{STANDARD_THREEMA_PREFIX}_{entLogin}"
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
                        print(f"Overriding entry for {entLogin} with user Id {u.get('id')}")
                    
                threemaUserIdForENTLogin[entLogin] = u.get("id")
                lastLoginDate = u.get("lastCheck")
                
        
        if not threemaUserIdForENTLogin.get(entLogin):
            print(f"No active threema user yet for ent login {entLogin}")
    else:
        print(f"WARNING: ENT user {entLogin} has no threema credentials yet!")

teacher_threema_user_ids = set(threemaUserIdForENTLogin.values())
print("\n\n\n***** STARTING GROUP SYNCHRONIZATION *****\n")

for teacher_group_id in TEACHER_GROUP_IDS:
    group_name = client.getGroupDetails(teacher_group_id).get("name")
    
    if not group_name:
        print(f"ERROR: Group ID {teacher_group_id} not found, please check entry in threema.yml")
        continue
    
    print(f"Synchronizing group with ID {teacher_group_id}. Group name is: {group_name}")
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
            new_members.append(tid)
        
    print(f"{log_prefix} The following members are ADDED to this group: {new_members}")
    print(f"{log_prefix} The following members are REMOVED from this group: {remove_members}")    
    
    if persist_changes:
        if new_members:
            try:
                client.addGroupMembers(groupId=teacher_group_id, members=new_members)
            except Exception as ex:
                print("ERROR while adding new members: ", ex)
            
        if remove_members:
            try:
                client.removeGroupMembers(groupId=teacher_group_id, memberIds=remove_members)
            except Exception as ex:
                print("ERROR while removing obsolete members: ", ex)
        
        
        
