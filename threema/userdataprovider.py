from aj.plugins.lmn_common.ldap.requests import LMNLdapRequests


class UserDataProvider():
    def getUserData(self):
        lr = LMNLdapRequests(None)
        users_data = lr.get('/role/student', school_oriented=False)
        users_data += lr.get('/role/teacher', school_oriented=False)
        return users_data
