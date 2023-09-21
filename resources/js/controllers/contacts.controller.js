angular.module("dfglfa.threema_connector").controller("ContactsController", function ($scope, $http, pageTitle, gettext, notify) {
  pageTitle.set(gettext("Contacts"));

  $scope.isUpdating = false;
  $scope.match = match;
  $scope.synchronize = synchronize;

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
  loadResults();

  function loadResults() {
    return Promise.all([
      $http.get("/api/threema_connector/credentials", {}),
      $http.get("/api/threema_connector/users", {}),
      $http.get("/api/threema_connector/contacts", {}),
    ]).then(([{ data: credentials }, { data: users }, { data: contacts }]) => {
      console.log("Credentials:", credentials);
      console.log("Users:", users);
      console.log("Contacts:", contacts);
    });
  }

  function matchUsers() {
    return $http.get("/api/threema_connector/users", {}).then(({ data: users }) => {
      const user_dict = {};
      for (const u of resp.data) {
        user_dict[u.id] = u;
      }
      $scope.user_dict = user_dict;

      for (const contact of $scope.contacts) {
        contact.matchingUsername = user_dict[contact.id] ? user_dict[contact.id].nickname : "NO MATCH";
      }
    });
  }

  function match() {
    return $http.get("/api/threema_connector/contacts/match").then(() => {
      notify.success(`Match done`);
    });
  }

  function synchronize() {
    $scope.isUpdating = true;
    return $http
      .post("/api/threema_connector/contacts/sync")
      .then(() => {
        notify.success(`Sync done`);
      })
      .then(loadResults);
  }
});
