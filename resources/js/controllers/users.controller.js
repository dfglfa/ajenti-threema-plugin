angular.module("dfglfa.threema_connector").controller("ThreemaUsersController", function ($scope, $http, $uibModal, gettext, notify) {
  $scope.users = undefined;
  $scope.paging = { pageSize: 50, page: 1 };

  $scope.orphans = [];
  $scope.openUserDeleteModal = openUserDeleteModal;

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
      const userdata = resp.data.concat({ id: 123, nickname: "hans" });

      const usage = {};
      for (const u of userdata) {
        if (usage[u.credentials_id]) {
          usage[u.credentials_id]++;
        } else {
          usage[u.credentials_id] = 1;
        }
      }

      const user_list = [];
      const orphans = [];
      for (const u of userdata) {
        creds_usage = usage[u.credentials_id];
        creds_id = credentials_dict[u.credentials_id];
        credentials_name_or_id = creds_id ? creds_id.username : u.credentials_id;

        if (!creds_id) {
          orphans.push(u);
        }

        user_list.push({
          ...u,
          credentials_name: credentials_name_or_id,
          usage: creds_usage,
        });
      }

      $scope.users = user_list;
      $scope.orphans = orphans;
    });
  }

  function openUserDeleteModal(users) {
    const modal = $uibModal.open({
      templateUrl: "/threema_connector:resources/partial/userDelete.modal.html",
      controller: "UserDeleteController",
      size: "lg",
      resolve: {
        users: () => users,
      },
    });

    modal.result.then(() => {
      const userIds = users.map((u) => u.id);
      notify.success(gettext("Deleted"));
      $scope.users = $scope.users.filter((c) => userIds.indexOf(c.id) === -1);
      $scope.orphans = $scope.orphans.filter((o) => userIds.indexOf(o.id) === -1);
    });
  }
});
