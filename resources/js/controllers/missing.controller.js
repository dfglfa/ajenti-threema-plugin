angular.module("example.threema_connector").controller("MissingController", function ($scope, $http, pageTitle, gettext, notify) {
  pageTitle.set(gettext("Missing"));

  $scope.isUpdating = false;
  $scope.add = addCredentials;
  $scope.addAll = addCredentialsForAll;

  // Check on page load
  $scope.results = undefined;
  loadResults();

  function loadResults() {
    return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
      $scope.results = resp.data;
    });
  }

  function addCredentials(username, reloadOnFinish) {
    $scope.isUpdating = true;
    return $http
      .put("/api/threema_connector/credentials", { username })
      .then(() => {
        notify.success(`User ${username} successfully created`);
        reloadOnFinish && loadResults();
      })
      .finally(() => ($scope.isUpdating = false));
  }

  function addCredentialsForAll() {
    const allTasks = [];
    for (let uname of $scope.results.unused) {
      allTasks.push(addCredentials(uname));
    }
    Promise.all(allTasks).then(() => {
      notify.success("All credentials created");
      loadResults();
    });
  }
});
