angular
  .module("example.threema_connector")
  .controller("CredentialsDeleteController", function ($scope, $http, $uibModalInstance, threemaId, username) {
    $scope.username = username;
    $scope.isDeleting = false;

    $scope.delete = () => {
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
    };

    $scope.cancel = () => {
      $uibModalInstance.dismiss();
    };
  });
