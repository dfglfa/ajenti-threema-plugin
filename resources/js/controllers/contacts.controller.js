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
    return $http.get("/api/threema_connector/contacts", {}).then((resp) => {
      $scope.contacts = resp.data;
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
