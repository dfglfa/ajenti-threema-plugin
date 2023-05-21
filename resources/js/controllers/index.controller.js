angular
  .module("example.threema_connector")
  .controller("ThreemaConnectorIndexController", function ($scope, $http, pageTitle, gettext, notify, $uibModal) {
    pageTitle.set(gettext("ThreemaConnector"));

    $scope.credentials = undefined;
    $scope.validated = false;
    $scope.isValidating = false;
    $scope.reverse = false;

    $scope.sorts = [
      { name: "Class", fx: (c) => classLevel(c.cls) },
      { name: "Name", fx: (c) => c.username },
      { name: "Validation", fx: (c) => validationLevel(c.status) },
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
        const cls = _getClass(c.username);
        creds.push({ id: c.id, cls, username: c.username });
      }

      $scope.credentials = creds;
    });

    $scope.validate = validate;
    $scope.openCredentialsChangeModal = openCredentialsChangeModal;
    $scope.openCredentialsDeleteModal = openCredentialsDeleteModal;

    function validate(credentialsSubset) {
      $scope.isValidating = true;
      const credentials = credentialsSubset || $scope.credentials;
      $http
        .post("/api/threema_connector/credentials/check", {
          idsToCheck: credentialsSubset ? credentialsSubset.map((c) => c.id) : null,
        })
        .then((resp) => {
          $scope.validated = true;
          const { ok, suggestions, unmatched } = resp.data;
          const ok_ids = ok.map((c) => c.id);
          const unmatched_ids = unmatched.map((c) => c.id);
          const suggestions_ids = suggestions.map((c) => c.id);

          for (let cred of credentials) {
            if (ok_ids.indexOf(cred.id) > -1) {
              cred.status = "OK";
            } else if (unmatched_ids.indexOf(cred.id) > -1) {
              cred.status = "UNMATCHED";
            } else if (suggestions_ids.indexOf(cred.id) > -1) {
              cred.status = "SUGGESTION";
              cred.suggestions = suggestions.find((c) => c.id == cred.id).matches.map((m) => m[0]);
            } else {
              cred.status = "UNKNOWN";
            }
          }
        })
        .finally(() => ($scope.isValidating = false));
    }

    function openCredentialsChangeModal(threemaId, oldName, newName) {
      const modal = $uibModal.open({
        templateUrl: "/threema_connector:resources/partial/credentialsChange.modal.html",
        controller: "CredentialsChangeController",
        size: "lg",
        resolve: {
          threemaId: () => threemaId,
          oldName: () => oldName,
          newName: () => newName,
        },
      });

      modal.result.then((newName) => {
        const changedCredentials = $scope.credentials.filter((c) => c.id == threemaId);
        if (changedCredentials.length !== 1) {
          console.error("Not exactly one match:" + changedCredentials);
        } else {
          const cred = changedCredentials[0];
          cred.username = newName;
          cred.cls = _getClass(newName);
          validate([cred]);
        }
      });
    }

    function openCredentialsDeleteModal(threemaId, username) {
      const modal = $uibModal.open({
        templateUrl: "/threema_connector:resources/partial/credentialsDelete.modal.html",
        controller: "CredentialsDeleteController",
        size: "lg",
        resolve: {
          threemaId: () => threemaId,
          username: () => username,
        },
      });

      modal.result.then(() => {
        notify.success(gettext("Deleted"));
        $scope.credentials = $scope.credentials.filter((c) => c.id !== threemaId);
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

    function validationLevel(status) {
      if (status === "SUGGESTION") {
        return 0;
      } else if (status === "UNMATCHED") {
        return 1;
      } else if (status === "OK") {
        return 2;
      } else {
        return 3;
      }
    }

    function _getClass(username) {
      return username.indexOf("_") !== -1 ? username.split("_")[0] : "?";
    }
  });
