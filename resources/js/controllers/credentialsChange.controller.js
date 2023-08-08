angular
  .module("dfglfa.threema_connector")
  .controller("CredentialsChangeController", function ($scope, $http, $uibModalInstance, threemaId, oldName, newName) {
    $scope.data = { oldName, newName };
    $scope.password = "";
    $scope.error = undefined;
    $scope.isUpdating = false;

    $scope.save = () => {
      $scope.isUpdating = true;
      $http
        .post("/api/threema_connector/credentials/update", {
          threemaId,
          changedName: $scope.data.newName,
          changedPassword: $scope.password,
        })
        .then(() => {
          $scope.isUpdating = false;
          $uibModalInstance.close($scope.data.newName);
        })
        .catch((err) => {
          $scope.isUpdating = false;
          $scope.error = err;
        });
    };

    $scope.cancel = () => {
      $uibModalInstance.dismiss();
    };
  });
