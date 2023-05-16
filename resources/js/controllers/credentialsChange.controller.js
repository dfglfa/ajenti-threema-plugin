angular.module("example.threema_connector").controller("CredentialsChangeController", function ($scope, $http, threemaId, oldName, newName) {
  $scope.username = newName;
  $scope.isUpdating = false;
});
