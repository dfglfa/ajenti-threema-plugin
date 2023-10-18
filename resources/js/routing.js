angular.module("dfglfa.threema_connector").config(($routeProvider) => {
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

  $routeProvider.when("/view/threema_connector/suggestions", {
    templateUrl: "/threema_connector:resources/partial/suggestions.html",
    controller: "SuggestionsController",
  });

  $routeProvider.when("/view/threema_connector/contactsSync", {
    templateUrl: "/threema_connector:resources/partial/normalizations.html",
    controller: "NormalizationsController",
  });

  $routeProvider.when("/view/threema_connector/groupCreation", {
    templateUrl: "/threema_connector:resources/partial/groupCreation.html",
    controller: "ThreemaGroupCreationController",
  });
});
