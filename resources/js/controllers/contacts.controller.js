angular.module("dfglfa.threema_connector").controller("ContactsController", function ($scope, $http, pageTitle, gettext, notify) {
  pageTitle.set(gettext("Contacts"));

  $scope.isUpdating = false;

  $scope.sorts = [
    { name: "First name", fx: (c) => c.firstName },
    { name: "Last name", fx: (c) => c.lastName },
    { name: "Active", fx: (c) => c.enabled },
  ];

  $scope.sort = $scope.sorts[0];
  $scope.paging = { pageSize: 20, page: 1 };

  $scope.sortClicked = (s) => {
    if ($scope.sort.name === s.name) {
      $scope.reverse = !$scope.reverse;
    } else {
      $scope.sort = s;
    }
  };

  // Check on page load
  $scope.contacts = undefined;
  loadResults().then(matchUsers);

  function loadResults() {
    return $http.get("/api/threema_connector/contacts", {}).then(({ data: contacts }) => {
      $scope.contacts = contacts;
    });
  }

  function matchUsers() {
    return $http.get("/api/threema_connector/users", {}).then(({ data: users }) => {
      const userDict = {};
      for (const u of users) {
        userDict[u.id] = u;
      }

      for (const c of $scope.contacts) {
        if (userDict[c.id]) {
          c.matchingUsername = userDict[c.id].nickname;
        }
      }
    });
  }
});
