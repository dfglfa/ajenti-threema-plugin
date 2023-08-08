angular
  .module("dfglfa.threema_connector")
  .controller("CredentialsDeleteController", function ($scope, $http, $uibModalInstance, threemaId, username, allUsers) {
    $scope.username = username;
    $scope.isDeleting = false;
    $scope.allUsers = allUsers;

    $scope.delete = () => {
      if (!allUsers) {
        $scope.isDeleting = true;

        $http
          .delete("/api/threema_connector/credentials/" + threemaId)
          .then(() => {
            $scope.isDeleting = false;
            $uibModalInstance.close();
          })
          .catch((err) => {
            $scope.isDeleting = false;
            $scope.error = err;
          });
      } else {
        $uibModalInstance.close();
      }
    };

    $scope.cancel = () => {
      $uibModalInstance.dismiss();
    };
  });
