angular.module("example.threema_connector").controller("ThreemaConnectorConcistencyController", function ($scope, $http, pageTitle, gettext, notify) {
  pageTitle.set(gettext("Consistency"));

  $scope.updatePending = false;

  check();

  $scope.applySuggestion = (threemaId, changedName) => {
    $scope.updatePending = true;
    $http
      .post("/api/threema_connector/credentials/update", {
        threemaId,
        changedName,
      })
      .then((resp) => {
        $scope.check().then(() => {
          $scope.updatePending = false;
        });
      })
      .catch(() => {
        $scope.updatePending = false;
      });
  };

  function check() {
    return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
      $scope.results = resp.data;
    });
  }
});
