import json


class User:
    def __init__(self, **userData):
        """
        :param userData: Threema response parsed from JSON.

        Example:
        {
            "id": "B4UXXX11", // UserID: 9964FH88
            "nickname": "Alice",
            "firstName": "Al",
            "lastName": "Ice",
            "csi": "AI000001",
            "category": "Marketing",
            "version": "android - 3.1k",
            "lastCheck": "2017-01-01T00:00:00+0100",
            "createdAt": "2017-01-01T00:00:00+0100"
        }
        """
        for key, val in userData.items():
            setattr(self, key, val)

    def __repr__(self):
        return f"{getattr(self, 'nickname', 'NONAME')}: ({getattr(self, 'firstName', 'NOFIRSTNAME')} {getattr(self, 'lastName', 'NOLASTNAME')}, ID: {self.id})"

    def toJsonDict(self):
        return {
            "id": self.id,
            "nickname": self.nickname,
            "firstname": self.firstname,
            "lastname": self.lastname
        }


class Credentials:
    """
    :param credentialsData: Threema response parsed from JSON.

    Note: The response seems to contain the key "usage" instead of 
    "licenseAmount" (from the documentation). 

    Example:

    {
        "_links": [...]
        "id": "LAow0Rksa",
        "username": "alice",
        "password": "3mawrk",
        "licenseAmount": 0,
        "usage": 1,
        "hash": false,
        "lock": tr
    }
    """

    def __init__(self, **credentialsData):
        for key, val in credentialsData.items():
            setattr(self, key, val)

    def __repr__(self):
        return f"Username: {self.username} ID: {self.id}"

    def __str__(self):
        return f"Username: {self.username:35} ID: {self.id}"

    def toJsonDict(self, includePasswords=False):
        d = {
            "id": self.id,
            "username": self.username,
            "licenseAmount": getattr(self, "licenseAmount", -1),
            "usage": getattr(self, "usage", -1)
        }
        if includePasswords:
            d["password"] = self.password
        return d
