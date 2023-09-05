angular.module("dfglfa.threema_connector").directive("groups", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/groups.html",
    controller: "ThreemaGroupsController",
  };
});
