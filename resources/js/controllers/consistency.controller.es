angular
  .module("example.threema_connector")
  .controller(
    "ThreemaConnectorConcistencyController",
    function ($scope, $http, pageTitle, gettext, notify) {
      pageTitle.set(gettext("Consistency"));

      $scope.check = () => {
        $http.get("/api/threema_connector/credentials/check").then((resp) => {
          $scope.results = resp.data;
        });
      };

      $scope.applySuggestion = (threemaId, changedName) => {
        $http
          .post("/api/threema_connector/credentials/update", {
            threemaId,
            changedName,
          })
          .then((resp) => {
            $scope.check();
          });
      };
    }
  );
