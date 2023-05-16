angular.module("example.threema_connector").controller("ThreemaConnectorIndexController", function ($scope, $http, pageTitle, gettext, notify) {
  pageTitle.set(gettext("ThreemaConnector"));

  $scope.credentials = undefined;
  $scope.reverse = false;

  $scope.sorts = [
    { name: "Klasse", fx: (c) => classLevel(c.cls) },
    { name: "Name", fx: (c) => c.username },
  ];

  $scope.sort = $scope.sorts[0];
  $scope.paging = { pageSize: 20, page: 0 };

  $scope.sortClicked = (s) => {
    if ($scope.sort.name === s.name) {
      $scope.reverse = !$scope.reverse;
    } else {
      $scope.sort = s;
    }
  };

  // GET a result through Python API
  $http.get("/api/threema_connector/credentials").then((resp) => {
    const creds = [];

    for (let c of resp.data) {
      const [cls, username] = c.username.indexOf("_") !== -1 ? c.username.split("_") : ["?", c.username];

      creds.push({ cls, username });
    }

    $scope.credentials = creds;
  });

  function classLevel(c) {
    if (c === "?") {
      return -1;
    } else if (c.startsWith("T")) {
      return 12;
    } else {
      if (c.startsWith("5")) {
        if (c.startsWith("5I")) {
          return 7;
        } else {
          return 5;
        }
      } else if (c.match("^[1-9]")) {
        if (c.match("^[1-9][ab]")) {
          return +c[0];
        } else {
          return 12 - c[0];
        }
      } else {
        console.error("Unrecognized class:", c);
        return -1;
      }
    }
  }
});
