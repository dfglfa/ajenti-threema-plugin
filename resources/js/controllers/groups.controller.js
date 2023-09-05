angular.module("dfglfa.threema_connector").controller("ThreemaGroupsController", function ($scope, $http) {
  $scope.selectedClass = undefined;
  $scope.select = (cls) => {
    if (cls) {
      $scope.students = undefined;
      $scope.selectedClass = cls;
      $http.get("/api/threema_connector/credentials_with_passwords", { params: { classname: cls } }).then((resp) => {
        $scope.students = resp.data;
        loadUserData();
      });
    } else {
      $scope.selectedClass = undefined;
    }
  };

  $scope.toggleVisibility = (studentId) => {
    $scope.students.forEach((s) => {
      if (s.id === studentId) {
        s.showPassword = !s.showPassword;
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
    let content = "Benutzername,Passwort\n";
    $scope.students.forEach((s) => {
      content += `${s.username},${s.password}\n`;
    });
    createAndDownloadTextFile(content, `passwords_${$scope.selectedClass}.csv`);
  };

  function loadUserData() {
    for (const sd of $scope.students) {
      if (sd.usage > 0) {
        $http.get(`/api/threema_connector/users?filterUsername=${sd.username}`).then((resp) => {
          const linkedUsers = resp.data;
          if (linkedUsers && linkedUsers.length === 1) {
            sd.nickname = linkedUsers[0].nickname;
          } else {
            console.error("No user data found for active credentials", sd);
          }
        });
      }
    }
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
});
