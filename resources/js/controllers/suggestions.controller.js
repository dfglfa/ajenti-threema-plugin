angular.module("example.threema_connector").controller("SuggestionsController", function ($scope, $http, $uibModal, pageTitle, gettext, notify) {
  $scope.isUpdating = false;
  $scope.apply = applySuggestion;
  $scope.applyAll = applyAllSuggestions;

  // Check on page load
  $scope.results = undefined;
  loadResults();

  function loadResults() {
    return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
      $scope.results = resp.data;
    });
  }

  function applySuggestion(threemaId, newName, reloadOnFinish) {
    $scope.isUpdating = true;
    return $http
      .post("/api/threema_connector/credentials/update", {
        threemaId,
        changedName: newName,
      })
      .then(() => {
        notify.success(`User successfully renamed`);
        reloadOnFinish && loadResults();
      })
      .finally(() => ($scope.isUpdating = false));
  }

  function applyAllSuggestions() {
    const allTasks = [];
    for (let suggestion of $scope.results.suggestions) {
      allTasks.push(applySuggestion(suggestion.id, suggestion.matches[0][0]));
    }
    Promise.all(allTasks).then(() => {
      notify.success("Successfully renamed " + allTasks.length + " users.");
      loadResults();
    });
  }
});
