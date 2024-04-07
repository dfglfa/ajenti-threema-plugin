angular
  .module("dfglfa.threema_connector")
  .controller("MissingController", function ($scope, $http, $timeout, pageTitle, gettext, notify, classService) {
    pageTitle.set(gettext("Missing"));

    $scope.isUpdating = false;
    $scope.add = addCredentials;
    $scope.addAll = addCredentialsForAll;

    // Check on page load
    $scope.results = undefined;
    loadResults();

    $scope.queue = [];
    $scope.done = 0;
    $scope.total = 0;

    $scope.THREEMA_PREFIX = "dfg";

    function loadResults() {
      return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
        $scope.results = resp.data;
      });
    }

    function addCredentials(entLogin, singleUpdate) {
      if (singleUpdate) {
        $scope.isUpdating = true;
      }

      const threemaUsername = $scope.THREEMA_PREFIX + "_" + entLogin;

      return $http
        .put("/api/threema_connector/credentials", { username: threemaUsername })
        .then(() => {
          notify.success(`User ${threemaUsername} successfully created`);
          singleUpdate && loadResults();
        })
        .finally(() => {
          if (singleUpdate) {
            $scope.isUpdating = false;
          }
        });
    }

    function addCredentialsForAll() {
      const allTasks = [];
      for (let uname of $scope.results.unused) {
        allTasks.push(uname);
      }

      $scope.isUpdating = true;
      $scope.queue = allTasks;
      $scope.total = allTasks.length;
      $scope.done = 0;
      processQueue();
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
        const newName = $scope.queue.pop();
        addCredentials(newName).then(() => {
          $scope.done++;
          $timeout(processQueue, 300);
        });
      }
    }
  });
