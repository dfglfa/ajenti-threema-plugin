angular.module("dfglfa.threema_connector").controller("ThreemaGroupsController", function ($scope, $http) {
  loadDataForAllGroups();

  function loadDataForAllGroups() {
    return $http.get("/api/threema_connector/groups").then(({ data: groups }) => {
      $scope.groups = groups;
    });
  }
});
