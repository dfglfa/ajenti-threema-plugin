angular.module("dfglfa.threema_connector").controller("UnmatchedController", function ($scope, $http, $uibModal, $timeout, notify, classService) {
  $scope.isUpdating = false;
  $scope.delete = deleteCredentials;
  $scope.deleteSelected = deleteSelectedCredentials;
  $scope.openCredentialsDeleteModal = openCredentialsDeleteModal;
  $scope.toggle = toggle;
  $scope.selectAll = selectAll;
  $scope.unselectAll = unselectAll;

  // Check on page load
  $scope.unmatchedCredentials = undefined;
  loadResults();

  $scope.queue = [];
  $scope.done = 0;
  $scope.total = 0;
  $scope.selectedIds = [];
  $scope.allIds = [];

  function loadResults() {
    return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
      const unmatchedCredentials = [];
      for (const user of resp.data.unmatched) {
        unmatchedCredentials.push(user);
      }
      $scope.unmatchedCredentials = unmatchedCredentials;
      $scope.selectedIds = unmatchedCredentials.map(c => c.id);
      $scope.allIds = $scope.selectedIds;
    });
  }

  function toggle(uid) {
    if ($scope.selectedIds.indexOf(uid) === -1) {
      $scope.selectedIds.push(uid);
    } else {
      $scope.selectedIds = $scope.selectedIds.filter(i => i !== uid);
    }
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
        multipleUsers: () => true,
      },
    });

    modal.result.then(deleteSelectedCredentials);
  }

  function deleteSelectedCredentials() {
    const allTasks = [];
    for (let unmatched of $scope.unmatchedCredentials) {
      if ($scope.selectedIds.indexOf(unmatched.id) > -1) {
        allTasks.push([unmatched.id, unmatched.username]);
      }
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

  function selectAll() {
    $scope.selectedIds = $scope.allIds;
  }

  function unselectAll() {
    $scope.selectedIds = [];
  }
});
