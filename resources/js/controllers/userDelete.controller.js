angular.module("dfglfa.threema_connector").controller("UserDeleteController", function ($scope, $http, $uibModalInstance, $timeout, users) {
  $scope.users = users;
  $scope.isDeleting = false;

  $scope.deleteUsers = deleteUsers;

  $scope.cancel = () => {
    $uibModalInstance.dismiss();
  };

  const idList = users.map((u) => u.id);

  function deleteUsers() {
    if (idList.length === 0) {
      $scope.isDeleting = false;
      $uibModalInstance.close();
      return;
    }

    $scope.isDeleting = true;
    const userId = idList.pop();
    deleteUser(userId).then(() => {
      $timeout(deleteUsers, 300);
    });
  }

  function deleteUser(userId) {
    return $http
      .delete("/api/threema_connector/users/" + userId)
      .then(() => {
        $uibModalInstance.close();
      })
      .catch((err) => {
        $scope.isDeleting = false;
        $scope.error = err;
      });
  }
});
