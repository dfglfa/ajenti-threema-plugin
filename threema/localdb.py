import os
import sys
import sqlite3

current_file_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_file_dir)
sys.path.append(parent_dir)

from threema.entuserdataprovider import ENTUserDataProvider
from threema.threemaapi import ThreemaAdminClient

threema_client = ThreemaAdminClient()
ent_user_data_provider = ENTUserDataProvider()

def fetch_data():
    with sqlite3.connect("local.db") as db:
        cursor = db.cursor()
        setup_tables(cursor)
        
        userdata = ent_user_data_provider.getUserData()
        for login, data in userdata.items():
            cursor.execute("""
                INSERT INTO ent_users (login, firstname, lastname, class)
                VALUES (?, ?, ?, ?);
            """, (login, data["firstName"], data["lastName"], data["cls"]))

        credentials = threema_client.getAllCredentials(json=True)
        for cred in credentials:
            cursor.execute("""
                INSERT INTO credentials (credentials_id, credentials_name, usage, hashed, locked)
                VALUES (?, ?, ?, ?, ?)
            """, (cred["id"], cred["username"], cred["usage"], cred["hashed"], cred["locked"]))

        users = threema_client.getAllUsers()
        for user in users:
            cursor.execute("""
                INSERT INTO users (userid, credentials_id, nickname, firstname, lastname, createdAt, lastCheck)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user["id"], user["credentials_id"], user["nickname"], user["firstName"], user["lastName"], user["createdAt"], user["lastCheck"]))

        contacts = threema_client.getContacts()
        for contact in contacts:
            cursor.execute("""
                INSERT INTO contacts (userid, firstname, lastname, enabled)
                VALUES (?, ?, ?, ?)
            """, (contact["id"], contact["firstName"], contact["lastName"], contact["enabled"]))

def get_user_table():
    with sqlite3.connect("local.db") as db:
        cursor = db.cursor()
        cursor.execute("""
            select * from ent_users
            left outer join credentials on credentials_name = login
            left outer join users on users.credentials_id = credentials.credentials_id
            left outer join contacts on users.userid = contacts.userid
            order by class;
        """)
        return cursor.fetchall()

def setup_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "ent_users" (
        "login"	TEXT UNIQUE,
        "firstname"	TEXT NOT NULL,
        "lastname"	TEXT NOT NULL,
        "class"	TEXT NOT NULL,
        PRIMARY KEY("login")
    );""")

    cursor.execute("DELETE FROM ent_users")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "credentials" (
        "credentials_id" TEXT,
        "credentials_name" TEXT NOT NULL,
        "password" TEXT,
        "usage" INTEGER,
        "hashed" INTEGER,
        "locked" INTEGER,
        PRIMARY KEY("credentials_id")
    );""")

    cursor.execute("DELETE FROM credentials")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "users" (
        "userid" TEXT NOT NULL,
        "credentials_id" TEXT,
        "nickname" TEXT,
        "firstname" TEXT,
        "lastname" TEXT,
        "createdAt" TEXT,
        "lastCheck" TEXT,
        PRIMARY KEY("userid")
    );""")

    cursor.execute("DELETE FROM users")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "contacts" (
        "userid" TEXT NOT NULL,
        "firstname" TEXT,
        "lastname" TEXT,
        "enabled" INTEGER,
        PRIMARY KEY("userid")
    );""")

    cursor.execute("DELETE FROM contacts")

if __name__ == "__main__":
    fetch_data()
