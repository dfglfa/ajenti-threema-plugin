angular.module("dfglfa.threema_connector").controller("ThreemaPasswordsController", function ($scope, $http, classService) {
  $scope.selectedGroup = undefined;
  $scope.selectGroup = selectGroup;
  $scope.toggleVisibility = toggleVisibility;
  $scope.downloadPasswordList = downloadPasswordList;

  $scope.classesForLevel = {
    5: ["5a", "5b"],
    6: ["6a", "6b", "6eI", "6eII"],
    7: ["7a", "7b", "5eI", "5eII"],
    8: ["8a", "8b", "4eI", "4eII"],
    9: ["9a", "9b", "3eI", "3eII"],
    10: ["2L1", "2L2", "2ES", "2S1", "2S2"],
    11: ["1L1", "1L2", "1ES", "1SMP", "1SBC1", "1SBC2"],
    12: ["TL1", "TL2", "TES", "TSMP", "TSBC1", "TSBC2"],
  };

  function selectGroup(group) {
    if (group) {
      $scope.selectedGroup = group;
      loadStudentsDataForSelectedGroup();
    } else {
      $scope.selectedGroup = undefined;
    }
  }

  function loadStudentsDataForSelectedGroup() {
    $scope.students = undefined;
    return $http.get("/api/threema_connector/credentials_with_passwords", { params: { classname: $scope.selectedGroup } }).then((resp) => {
      $scope.students = resp.data;
      $scope.activeMembers = $scope.students.filter((s) => s.usage > 0);
    });
  }

  function createAndDownloadTextFile(textContent, filename) {
    const blob = new Blob([textContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function downloadPasswordList() {
    let content = "Benutzername,Passwort\n";
    $scope.students.forEach((s) => {
      content += `${s.username},${s.password}\n`;
    });
    createAndDownloadTextFile(content, `passwords_${$scope.selectedGroup}.csv`);
  }

  function toggleVisibility(studentId) {
    $scope.students.forEach((s) => {
      if (s.id === studentId) {
        s.showPassword = !s.showPassword;
      }
    });
  }
});
