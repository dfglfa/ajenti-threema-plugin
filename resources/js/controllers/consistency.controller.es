angular
  .module("example.threema_connector")
  .controller(
    "ThreemaConnectorConcistencyController",
    function ($scope, $http, pageTitle, gettext, notify) {
      pageTitle.set(gettext("Consistency"));

      $scope.correct = [];
      $scope.incorrect = [];
      $scope.nodb = [];
      $scope.unused = [];

      $scope.check = () => {
        $http.get("/api/threema_connector/credentials/check").then((resp) => {
          $scope.python_get = resp.data;
        });
      };
    }
  );
