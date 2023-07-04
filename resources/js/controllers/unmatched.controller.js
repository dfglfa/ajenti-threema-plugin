angular.module("example.threema_connector").controller("UnmatchedController", function ($scope, $http, $uibModal, pageTitle, gettext, notify) {
  $scope.isUpdating = false;
  $scope.delete = deleteCredentials;
  $scope.deleteAll = deleteAllCredentials;
  $scope.openCredentialsDeleteModal = openCredentialsDeleteModal;

  // Check on page load
  $scope.results = undefined;
  loadResults();

  function loadResults() {
    return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
      $scope.results = resp.data;
    });
  }

  function deleteCredentials(threemaId, username, reloadOnFinish) {
    $scope.isUpdating = true;
    return $http
      .delete("/api/threema_connector/credentials/" + threemaId)
      .then(() => {
        notify.success(`Threema user ${username} successfully deleted`);
        reloadOnFinish && loadResults();
      })
      .finally(() => ($scope.isUpdating = false));
  }

  function deleteAllCredentials() {
    const allTasks = [];
    for (let unmatched of $scope.results.unmatched) {
      allTasks.push(deleteCredentials(unmatched.id, unmatched.username));
    }
    Promise.all(allTasks).then(() => {
      notify.success("Successfully deleted " + allTasks.length + " unmatched credentials.");
      loadResults();
    });
  }

  function openCredentialsDeleteModal() {
    const modal = $uibModal.open({
      templateUrl: "/threema_connector:resources/partial/credentialsDelete.modal.html",
      controller: "CredentialsDeleteController",
      size: "lg",
      resolve: {
        threemaId: () => undefined,
        username: () => "ALL users",
      },
    });

    modal.result.then(deleteAllCredentials);
  }
});
