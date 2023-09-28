angular.module("dfglfa.threema_connector").directive("passwords", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/passwords.html",
    controller: "ThreemaPasswordsController",
  };
});
