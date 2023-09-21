angular.module("dfglfa.threema_connector").controller("ThreemaGroupsController", function ($scope, $http) {
  $scope.selectedClass = undefined;

  // Global dict with classNames as keys if group exists and current members as a list of userids
  $scope.threemaGroupMembers = {};
  $scope.groupIdForName = {};

  $scope.selectClass = selectClass;
  $scope.toggleVisibility = toggleVisibility;
  $scope.downloadPasswordList = downloadPasswordList;
  $scope.createGroupWithActiveMembers = createGroupWithActiveMembers;
  $scope.addAllMissingActiveMembersToGroup = addAllMissingActiveMembersToGroup;

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

  loadDataForAllGroups();

  function selectClass(cls) {
    if (cls) {
      $scope.selectedClass = cls;
      reloadStudentsDataForSelectedClass().then(loadMembersForSelectedClass);
    } else {
      $scope.selectedClass = undefined;
    }
  }

  function reloadStudentsDataForSelectedClass() {
    $scope.students = undefined;
    return $http.get("/api/threema_connector/credentials_with_passwords", { params: { classname: $scope.selectedClass } }).then((resp) => {
      $scope.students = resp.data;
      $scope.activeMembers = $scope.students.filter((s) => s.usage > 0);
      $scope.groupExists = $scope.existingGroupNames.indexOf($scope.selectedClass) > -1;
      loadMatchingUserDataForListedCredentials();
    });
  }

  function loadDataForAllGroups() {
    return $http.get("/api/threema_connector/groups").then(({ data: groups }) => {
      $scope.existingGroupNames = groups.map((g) => g.name);
      for (const group of groups) {
        $scope.groupIdForName[group.name] = group.id;
      }
    });
  }

  function loadMembersForSelectedClass() {
    if ($scope.selectedClass && $scope.existingGroupNames.indexOf($scope.selectedClass) > -1) {
      const selectedGroupId = $scope.groupIdForName[$scope.selectedClass];
      $http.get(`/api/threema_connector/group_members?groupId=${selectedGroupId}`).then(({ data: members }) => {
        $scope.threemaGroupMembers[$scope.selectedClass] = members.map((m) => m.id);
        $scope.activeMembersMissingInGroup = $scope.students.filter(
          (s) => s.usage > 0 && $scope.threemaGroupMembers[$scope.selectedClass].indexOf(s.userid) === -1
        );
      });
    }
  }

  function loadMatchingUserDataForListedCredentials() {
    return $http.get("/api/threema_connector/users").then(({ data: users }) => {
      const userForCreds = {};

      for (const u of users) {
        userForCreds[u.credentials_id] = u;
      }

      for (const sd of $scope.students) {
        if (sd.usage > 0 && userForCreds[sd.id]) {
          sd.nickname = userForCreds[sd.id].nickname;
          sd.userid = userForCreds[sd.id].id;
        }
      }
    });
  }

  function createGroupWithActiveMembers() {
    return $http
      .post("/api/threema_connector/groups", { name: $scope.selectedClass, members: $scope.students.filter((s) => s.usage > 0).map((s) => s.userid) })
      .then(() => {
        loadDataForAllGroups().then(reloadStudentsDataForSelectedClass);
      });
  }

  function addAllMissingActiveMembersToGroup() {
    const selectedGroupId = $scope.groupIdForName[$scope.selectedClass];
    const members = $scope.students.filter((s) => s.usage > 0 && $scope.threemaGroupMembers[$scope.selectedClass].indexOf(s.userid) === -1);
    console.log("Adding members", members, "to group with id", selectedGroupId);
    return $http.post("/api/threema_connector/group_members", { groupId: selectedGroupId, members: members }).then(() => {
      reloadStudentsDataForSelectedClass();
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
    createAndDownloadTextFile(content, `passwords_${$scope.selectedClass}.csv`);
  }

  function toggleVisibility(studentId) {
    $scope.students.forEach((s) => {
      if (s.id === studentId) {
        s.showPassword = !s.showPassword;
      }
    });
  }
});
