angular.module("dfglfa.threema_connector").controller("ThreemaPasswordsController", function ($scope, $http) {
  $scope.selectedClass = undefined;
  $scope.select = (cls) => {
    if (cls) {
      $scope.students = undefined;
      $scope.selectedClass = cls;
      $http.get("/api/threema_connector/credentials_with_passwords", { params: { classname: cls } }).then((resp) => {
        $scope.students = resp.data;
      });
    } else {
      $scope.selectedClass = undefined;
    }
  };

  $scope.showPassword = (studentId) => {
    $scope.students.forEach((s) => {
      if (s.id === studentId) {
        s.showPassword = true;
      }
    });
  };

  $scope.classesForLevel = {
    5: ["5a", "5b"],
    6: ["6a", "6b", "6I", "6II"],
    7: ["7a", "7b", "5I", "5II"],
    8: ["8a", "8b", "4I", "4II"],
    9: ["9a", "9b", "3I", "3II"],
    10: ["2L1", "2L2", "2ES", "2S1", "2S2"],
    11: ["1L1", "1L2", "1ES", "1SMP", "1SBC1", "1SBC2"],
    12: ["TL1", "TL2", "TES", "TSMP", "TSBC1", "TSBC2"],
  };

  $scope.downloadPasswordList = () => {
    const content = $scope.students.map((s) => `Benutzername: ${s.username}\nPasswort: ${s.password}`).join("\n\n");
    createAndDownloadTextFile(content, `passwords_${$scope.selectedClass}.txt`);
  };

  function createAndDownloadTextFile(textContent, filename) {
    const blob = new Blob([textContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }
});
