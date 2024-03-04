angular.module("dfglfa.threema_connector").controller("ThreemaUsersController", function ($scope, $http, classService) {
  $scope.users = undefined;

  $scope.sorts = [
    { name: "Usage", fx: (c) => c.usage },
    { name: "Name", fx: (c) => c.nickname },
  ];

  $scope.sort = $scope.sorts[0];
  $scope.paging = { pageSize: 20, page: 1 };

  loadUsers();

  function loadUsers() {
    $http.get("/api/threema_connector/users").then((resp) => {
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
          usage: usage[u.credentials_id],
        });
      }

      $scope.users = user_list;
    });
  }
});
