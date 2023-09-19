angular.module("dfglfa.threema_connector").directive("contacts", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/contacts.html",
    controller: "ContactsController",
  };
});
