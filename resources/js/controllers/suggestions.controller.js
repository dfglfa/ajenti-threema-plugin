angular.module("dfglfa.threema_connector").controller("SuggestionsController", function ($scope, $http, $timeout, notify) {
  $scope.isUpdating = false;
  $scope.apply = applySuggestion;
  $scope.applyAll = applyAllSuggestions;

  $scope.queue = [];
  $scope.done = 0;
  $scope.total = 0;

  // Check on page load
  $scope.results = undefined;
  loadResults();

  function loadResults() {
    return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
      let suggestions = [];
      for (let entry of resp.data.matched) {
        if (entry.needsChange) {
          suggestions.push(entry);
        }
      }
      $scope.suggestions = suggestions;
      console.log("Suggestions: ", $scope.suggestions);
    });
  }

  function applySuggestion(threemaId, newName, singleUpdate) {
    if (singleUpdate) {
      $scope.isUpdating = true;
    }

    return $http
      .post("/api/threema_connector/credentials/update", {
        threemaId,
        changedName: newName,
      })
      .then(() => {
        notify.success(`User successfully renamed to ${newName}`);
        singleUpdate && loadResults();
      })
      .catch(() => {
        notify.error(`Error renaming user to ${newName}`);
      })
      .finally(() => {
        if (singleUpdate) {
          $scope.isUpdating = false;
        }
      });
  }

  function applyAllSuggestions() {
    const allTasks = [];
    for (let suggestion of $scope.suggestions) {
      allTasks.push([suggestion.id, suggestion.entLogin]);
    }

    $scope.isUpdating = true;
    $scope.queue = allTasks;
    $scope.total = allTasks.length;
    $scope.done = 0;
    $timeout(processQueue, 1000);
  }

  function processQueue() {
    if ($scope.queue.length === 0) {
      $timeout(() => {
        $scope.total = 0;
        $scope.done = 0;
        $scope.isUpdating = false;
        loadResults();
      }, 500);
    } else {
      const [threemaId, newName] = $scope.queue.pop();
      applySuggestion(threemaId, newName).then(() => {
        $scope.done++;
        $timeout(processQueue, 500);
      });
    }
  }
});
