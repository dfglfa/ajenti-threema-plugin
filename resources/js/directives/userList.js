angular.module("dfglfa.threema_connector").directive("userList", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/userList.html",
    controller: "ThreemaUserListController",
  };
});
