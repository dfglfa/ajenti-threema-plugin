angular.module("dfglfa.threema_connector").controller("ThreemaConnectorIndexController", function ($scope, $http, classService) {
  $scope.activetab = 0;

  loadCredentials();

  function loadCredentials() {
    $http.get("/api/threema_connector/credentials").then((resp) => {
      sortByUserType(resp.data);
    });
  }

  function sortByUserType(credsList) {
    const studentsCreds = [];
    const teachersCreds = [];

    for (let c of credsList) {
      if (c.username && classService.getClass(c.username)) {
        studentsCreds.push(c);
      } else {
        // Teachers have no class :o)
        teachersCreds.push(c);
      }
    }

    $scope.studentsCredentials = studentsCreds;
    $scope.teachersCredentials = teachersCreds;
  }

  $scope.onCredsChange = () => {
    sortByUserType($scope.studentsCredentials.concat($scope.teachersCredentials));
  };
});
