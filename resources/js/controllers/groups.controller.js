angular.module("dfglfa.threema_connector").controller("ThreemaGroupsController", function ($scope, $http, classService) {
  $scope.selectedGroup = undefined;

  // Global dict with classNames as keys if group exists and current members as a list of userids
  $scope.threemaGroupMembers = {};
  $scope.groupIdForName = {};
  $scope.otherGroups = [];

  $scope.selectGroup = selectGroup;
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

  const CLASS_NAMES = classService.getClassNames();

  loadDataForAllGroups();

  function selectGroup(group) {
    if (group) {
      $scope.selectedGroup = group;
      loadStudentsDataForSelectedGroup().then(loadMembersForSelectedGroup);
    } else {
      $scope.selectedGroup = undefined;
    }
  }

  function loadStudentsDataForSelectedGroup() {
    $scope.students = undefined;
    return $http.get("/api/threema_connector/credentials_with_passwords", { params: { classname: $scope.selectedGroup } }).then((resp) => {
      $scope.students = resp.data;
      $scope.activeMembers = $scope.students.filter((s) => s.usage > 0);
      $scope.groupExists = $scope.existingGroupNames.indexOf($scope.selectedGroup) > -1;
      loadMatchingUserDataForListedCredentials();
    });
  }

  function loadDataForAllGroups() {
    return $http.get("/api/threema_connector/groups").then(({ data: groups }) => {
      $scope.existingGroupNames = groups.map((g) => g.name);
      const otherGroups = [];
      for (const group of groups) {
        $scope.groupIdForName[group.name] = group.id;

        if (CLASS_NAMES.indexOf(group.name) === -1) {
          otherGroups.push(group);
        }
      }

      $scope.otherGroups = otherGroups;
    });
  }

  function loadMembersForSelectedGroup() {
    if ($scope.selectedGroup && $scope.existingGroupNames.indexOf($scope.selectedGroup) > -1) {
      const selectedGroupId = $scope.groupIdForName[$scope.selectedGroup];
      $http.get(`/api/threema_connector/group_members?groupId=${selectedGroupId}`).then(({ data: users }) => {
        const credentialsAlreadyListed = $scope.students.map((s) => s.id);
        console.log("Listed", credentialsAlreadyListed);
        for (const u of users) {
          if (credentialsAlreadyListed.indexOf(u.credentials_id) === -1) {
            console.log(u.credentials_id, "is not yet listed in", credentialsAlreadyListed);
            $scope.students.push({ username: "?", nickname: u.nickname, id: u.id });
          }
        }

        $scope.threemaGroupMembers[$scope.selectedGroup] = users.map((m) => m.id);
        $scope.activeMembersMissingInGroup = $scope.students.filter(
          (s) => s.usage > 0 && $scope.threemaGroupMembers[$scope.selectedGroup].indexOf(s.userid) === -1
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
      .post("/api/threema_connector/groups", { name: $scope.selectedGroup, members: $scope.students.filter((s) => s.usage > 0).map((s) => s.userid) })
      .then(() => {
        loadDataForAllGroups().then(reloadStudentsDataForselectedGroup);
      });
  }

  function addAllMissingActiveMembersToGroup() {
    const selectedGroupId = $scope.groupIdForName[$scope.selectedGroup];
    const members = $scope.students.filter((s) => s.usage > 0 && $scope.threemaGroupMembers[$scope.selectedGroup].indexOf(s.userid) === -1);
    console.log("Adding members", members, "to group with id", selectedGroupId);
    return $http.post("/api/threema_connector/group_members", { groupId: selectedGroupId, members: members }).then(() => {
      reloadStudentsDataForselectedGroup();
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
