angular.module("dfglfa.threema_connector").controller("ThreemaUsersController", function ($scope, $http) {
  $scope.users = undefined;
  $scope.paging = { pageSize: 50, page: 1 };

  const credentials_dict = {};
  loadCredentials().then(loadUsers);

  function loadCredentials() {
    return $http.get("/api/threema_connector/credentials").then((resp) => {
      for (const cred of resp.data) {
        credentials_dict[cred.id] = cred;
      }
      console.log("Dict:", credentials_dict);
    });
  }

  function loadUsers() {
    return $http.get("/api/threema_connector/users").then((resp) => {
      const userdata = resp.data;

      const usage = {};
      for (const u of userdata) {
        if (usage[u.credentials_id]) {
          usage[u.credentials_id]++;
        } else {
          usage[u.credentials_id] = 1;
        }
      }

      const user_list = [];
      for (const u of userdata) {
        user_list.push({
          ...u,
          credentials_name: credentials_dict[u.credentials_id]?.username,
          usage: usage[u.credentials_id],
        });
      }

      $scope.users = user_list;
    });
  }
});
