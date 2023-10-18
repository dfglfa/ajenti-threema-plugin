angular.module("dfglfa.threema_connector").controller("CSVUploadController", function ($scope, $uibModalInstance) {
  $scope.processFile = () => {
    var fileInput = document.getElementById("fileInput");
    var file = fileInput.files[0];
    console.log("Reading file", file);
    $uibModalInstance.close({ file });
  };

  $scope.cancel = () => {
    $uibModalInstance.dismiss();
  };
});
