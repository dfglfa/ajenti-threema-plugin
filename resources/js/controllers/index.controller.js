angular.module("dfglfa.threema_connector").controller("ThreemaConnectorIndexController", function ($scope, $http, $location, classService) {
  let queryParams = $location.search();
  $scope.activetab = +queryParams.active || 0;

  loadCredentials();

  function loadCredentials() {
    $http.get("/api/threema_connector/credentials").then((resp) => {
      sortByUserType(resp.data);
    });
  }

  function sortByUserType(credentials) {
    const studentsCreds = [];
    const teachersCreds = [];

    for (let c of credentials) {
      if (c.username && classService.getClass(c.username)) {
        studentsCreds.push(c);
      } else {
        // Teachers have no class :o)
        teachersCreds.push(c);
      }
    }

    $scope.studentsCredentials = studentsCreds;
    $scope.teachersCredentials = teachersCreds;
    $scope.credentials = credentials;
  }

  $scope.onCredsChange = () => {
    sortByUserType($scope.studentsCredentials.concat($scope.teachersCredentials));
  };
});
