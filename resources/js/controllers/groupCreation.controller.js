angular.module("dfglfa.threema_connector").controller("ThreemaGroupCreationController", function ($scope, $http, $timeout, $location) {
  $scope.groupId = $location.search().id;
  $scope.groupName = undefined;
  $scope.members = undefined;
  $scope.searching = false;
  $scope.maxResults = 30;

  $scope.searchContacts = searchContacts;
  $scope.createGroup = createGroup;
  $scope.addResults = addResults;
  $scope.loadMembers = loadMembers;

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
    $scope.members = [];
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
        for (const c of contacts) {
          if (!c.enabled) {
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
    const alreadyAdded = $scope.members.map((m) => m.id);
    for (const r of $scope.results) {
      if (alreadyAdded.indexOf(r.id) === -1) {
        members.push(r);
      }
    }
    $scope.members = $scope.members.concat(members);
    $scope.search = "";
    $scope.results = [];
  }

  function createGroup() {
    return $http.post("/api/threema_connector/groups", { name: $scope.groupName, members: $scope.members.map((m) => m.id) }).then(() => {
      $location.path("/view/threema_connector");
      console.log("Group successfully created");
    });
  }

  function loadMembers() {
    return $http.get(`/api/threema_connector/group_members`, { params: { groupId: $scope.groupId } }).then(({ data: members }) => {
      const mems = [];
      for (const m of members) {
        mems.push({ id: m.id, firstName: m.firstName, lastName: m.lastName });
      }
      $scope.members = mems;
    });
  }

  function loadGroupInfo() {
    return $http.get(`/api/threema_connector/group_details`, { params: { groupId: $scope.groupId } }).then(({ data }) => {
      $scope.groupName = data.name;
    });
  }
});
