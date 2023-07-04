angular.module("example.threema_connector").config(($routeProvider) => {
  $routeProvider.when("/view/threema_connector", {
    templateUrl: "/threema_connector:resources/partial/index.html",
    controller: "ThreemaConnectorIndexController",
  });

  $routeProvider.when("/view/threema_connector/missing", {
    templateUrl: "/threema_connector:resources/partial/missing.html",
    controller: "MissingController",
  });

  $routeProvider.when("/view/threema_connector/unmatched", {
    templateUrl: "/threema_connector:resources/partial/unmatched.html",
    controller: "UnmatchedController",
  });
});
