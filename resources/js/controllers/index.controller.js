angular
  .module("dfglfa.threema_connector")
  .constant("TEACHER_PREFIX", "L_")
  .controller("ThreemaConnectorIndexController", function ($scope, $http, TEACHER_PREFIX) {
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
        if (c.username && c.username.startsWith(TEACHER_PREFIX)) {
          teachersCreds.push(c);
        } else {
          studentsCreds.push(c);
        }
      }

      $scope.studentsCredentials = studentsCreds;
      $scope.teachersCredentials = teachersCreds;
    }

    $scope.onCredsChange = () => {
      sortByUserType($scope.studentsCredentials.concat($scope.teachersCredentials));
    };
  });
