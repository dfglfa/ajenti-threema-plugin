angular.module("example.threema_connector").controller("ThreemaConnectorIndexController", function ($scope, $http, pageTitle, gettext, notify) {
  pageTitle.set(gettext("ThreemaConnector"));

  $scope.credentials = undefined;
  $scope.validated = false;
  $scope.reverse = false;

  $scope.sorts = [
    { name: "Klasse", fx: (c) => classLevel(c.cls) },
    { name: "Name", fx: (c) => c.username },
  ];

  $scope.sort = $scope.sorts[0];
  $scope.paging = { pageSize: 20, page: 1 };

  $scope.sortClicked = (s) => {
    if ($scope.sort.name === s.name) {
      $scope.reverse = !$scope.reverse;
    } else {
      $scope.sort = s;
    }
  };

  $http.get("/api/threema_connector/credentials").then((resp) => {
    const creds = [];

    for (let c of resp.data) {
      const [cls, username] = c.username.indexOf("_") !== -1 ? c.username.split("_") : ["?", c.username];

      creds.push({ id: c.id, cls, username: c.username });
    }

    $scope.credentials = creds;
  });

  $scope.validate = validate;

  function validate() {
    $http.get("/api/threema_connector/credentials/check").then((resp) => {
      $scope.validated = true;
      const { ok, suggestions, unmatched, unused } = resp.data;
      const ok_ids = ok.map((c) => c.id);
      const unmatched_ids = unmatched.map((c) => c.id);
      const suggestions_ids = suggestions.map((c) => c.id);

      for (let cred of $scope.credentials) {
        if (ok_ids.indexOf(cred.id) > -1) {
          cred.status = "OK";
        } else if (unmatched_ids.indexOf(cred.id) > -1) {
          cred.status = "UNMATCHED";
        } else if (suggestions_ids.indexOf(cred.id) > -1) {
          cred.status = "SUGGESTION";
          cred.suggestions = suggestions.find((c) => c.id == cred.id).matches;
        } else {
          cred.status = "UNKNOWN";
        }
      }
    });
  }

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
