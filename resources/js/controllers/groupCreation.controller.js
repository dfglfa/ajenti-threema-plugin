angular.module("dfglfa.threema_connector").controller("ThreemaGroupCreationController", function ($scope, $http, $timeout, $location) {
  $scope.groupId = $location.search().id;
  $scope.groupName = undefined;
  $scope.existingMembers = undefined;
  $scope.newMembers = [];
  $scope.searching = false;
  $scope.maxResults = 30;

  $scope.searchContacts = searchContacts;
  $scope.createGroup = createGroup;
  $scope.updateGroupMembers = updateGroupMembers;
  $scope.addResults = addResults;
  $scope.loadMembers = loadMembers;
  $scope.addNewMember = addNewMember;
  $scope.removeNewMember = removeNewMember;
  $scope.removeFromGroup = removeFromGroup;
  $scope.triggerCSVUpload = triggerCSVUpload;
  $scope.processCSVFile = processCSVFile;

  let debounceTimer;
  function searchContacts() {
    if (debounceTimer) {
      $timeout.cancel(debounceTimer);
    }

    debounceTimer = $timeout(runSearch, 500);
  }

  if ($scope.groupId) {
    loadMembers();
    loadGroupInfo();
  } else {
    $scope.groupName = "";
    $scope.existingMembers = [];
  }

  function runSearch() {
    if (!$scope.search || $scope.search.length < 2) {
      $scope.results = [];
      return;
    }

    const searchTerm = $scope.search.toLowerCase();

    $scope.searching = true;
    return $http
      .get("/api/threema_connector/contacts", {})
      .then(({ data: contacts }) => {
        const results = [];
        const alreadyListed = $scope.existingMembers.concat($scope.newMembers).map((m) => m.id);
        for (const c of contacts) {
          if (!c.enabled || alreadyListed.indexOf(c.id) !== -1) {
            continue;
          }

          const searchtarget = `${c.firstName ? c.firstName.toLowerCase() : ""} ${c.lastName ? c.lastName.toLowerCase() : ""} ${c.id.toLowerCase()}`;
          if (searchtarget.indexOf(searchTerm) > -1) {
            results.push(c);
          }
        }

        $scope.results = results;
      })
      .finally(() => {
        $scope.searching = false;
      });
  }

  function addResults() {
    const members = [];
    const alreadyAdded = $scope.newMembers.map((m) => m.id);
    const existingIds = $scope.existingMembers.map((m) => m.id);
    for (const r of $scope.results) {
      if (alreadyAdded.indexOf(r.id) === -1 && existingIds.indexOf(r.id) === -1) {
        members.push(r);
      }
    }
    $scope.newMembers = $scope.newMembers.concat(members);
    runSearch();
  }

  function createGroup() {
    return $http.post("/api/threema_connector/groups", { name: $scope.groupName, members: $scope.newMembers.map((m) => m.id) }).then(() => {
      $location.url("/view/threema_connector?active=3");
      console.log("Group successfully created");
    });
  }

  function updateGroupMembers() {
    console.log("Updating id", $scope.groupId);
    return $http.post("/api/threema_connector/group_members", { groupId: $scope.groupId, members: $scope.newMembers.map((m) => m.id) }).then(() => {
      const existingMembers = $scope.existingMembers;
      for (const m of $scope.newMembers) {
        existingMembers.push(m);
      }
      $scope.newMembers = [];
      $scope.existingMembers = existingMembers;
    });
  }

  function loadMembers() {
    return $http.get(`/api/threema_connector/group_members`, { params: { groupId: $scope.groupId } }).then(({ data: members }) => {
      const mems = [];
      for (const m of members) {
        mems.push({ id: m.id, firstName: m.firstName, lastName: m.lastName });
      }
      $scope.existingMembers = mems;
    });
  }

  function addNewMember(m) {
    $scope.newMembers.push(m);
    $scope.results = $scope.results.filter((r) => r.id !== m.id);
  }

  function removeNewMember(m) {
    $scope.newMembers = $scope.newMembers.filter((nm) => nm.id !== m.id);
    runSearch();
  }

  function triggerCSVUpload() {
    document.getElementById("fileInput").click();
  }

  function processCSVFile() {
    var fileInput = document.getElementById("fileInput");
    var file = fileInput.files[0];
    console.log("Reading file", file);
    if (file) {
      var reader = new FileReader();

      // Define a callback for when the file is loaded
      reader.onload = function (e) {
        var fileContents = e.target.result;
        $http.post(`/api/threema_connector/group_members/csv`, { groupId: $scope.groupId, data: fileContents }).then(console.log);
      };

      reader.readAsText(file);
    } else {
      console.log("No file found");
    }
  }

  function removeFromGroup(memberId) {
    return $http.post(`/api/threema_connector/remove_group_members`, { groupId: $scope.groupId, memberIds: [memberId] }).then(() => {
      console.log("Deleted ", memberId);
      $scope.existingMembers = $scope.existingMembers.filter((m) => m.id !== memberId);
    });
  }

  function loadGroupInfo() {
    return $http.get(`/api/threema_connector/group_details`, { params: { groupId: $scope.groupId } }).then(({ data }) => {
      $scope.groupName = data.name;
    });
  }
});
