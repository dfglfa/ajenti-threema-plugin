angular.module("dfglfa.threema_connector").directive("credentials", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/credentials.html",
    controller: "CredentialsController",
  };
});
