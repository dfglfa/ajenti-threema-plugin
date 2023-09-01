angular.module("dfglfa.threema_connector").directive("teachersList", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/userList.html",
    controller: "ThreemaUserListController",
    scope: {
      credentials: "=",
      onCredentialsChange: "=",
    },
  };
});
