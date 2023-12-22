angular.module("dfglfa.threema_connector").directive("users", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/users.html",
    controller: "ThreemaUsersController",
  };
});
