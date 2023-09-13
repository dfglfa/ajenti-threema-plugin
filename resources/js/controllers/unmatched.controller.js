angular.module("dfglfa.threema_connector").controller("UnmatchedController", function ($scope, $http, $uibModal, $timeout, notify, classService) {
  $scope.isUpdating = false;
  $scope.delete = deleteCredentials;
  $scope.deleteAll = deleteAllCredentials;
  $scope.openCredentialsDeleteModal = openCredentialsDeleteModal;

  // Check on page load
  $scope.unmatchedStudents = undefined;
  $scope.unmatchedTeachers = undefined;
  loadResults();

  $scope.queue = [];
  $scope.done = 0;
  $scope.total = 0;

  function loadResults() {
    return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
      const unmatchedStudents = [];
      const unmatchedTeachers = [];
      for (const user of resp.data.unmatched) {
        if (user.username && classService.getClass(user.username)) {
          unmatchedStudents.push(user);
        } else {
          unmatchedTeachers.push(user);
        }
      }
      $scope.unmatchedStudents = unmatchedStudents;
      $scope.unmatchedTeachers = unmatchedTeachers;
    });
  }

  function deleteCredentials(threemaId, username, singleDelete) {
    if (singleDelete) {
      $scope.isUpdating = true;
    }

    return $http
      .delete("/api/threema_connector/credentials/" + threemaId)
      .then(() => {
        notify.success(`Threema user ${username} successfully deleted`);
        singleDelete && loadResults();
      })
      .finally(() => {
        if (singleDelete) {
          $scope.isUpdating = false;
        }
      });
  }

  function openCredentialsDeleteModal() {
    const modal = $uibModal.open({
      templateUrl: "/threema_connector:resources/partial/credentialsDelete.modal.html",
      controller: "CredentialsDeleteController",
      size: "lg",
      resolve: {
        threemaId: () => undefined,
        username: () => undefined,
        allUsers: () => true,
      },
    });

    modal.result.then(deleteAllCredentials);
  }

  function deleteAllCredentials() {
    const allTasks = [];
    for (let unmatched of $scope.unmatchedStudents) {
      allTasks.push([unmatched.id, unmatched.username]);
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
      const [threemaId, username] = $scope.queue.pop();
      deleteCredentials(threemaId, username).then(() => {
        $scope.done++;
        $timeout(processQueue, 500);
      });
    }
  }
});
