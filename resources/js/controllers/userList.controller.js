angular.module("dfglfa.threema_connector").controller("ThreemaUserListController", function ($scope, $http, pageTitle, gettext, notify, $uibModal) {
  pageTitle.set(gettext("ThreemaConnector"));

  $scope.credentials = undefined;
  $scope.reverse = false;

  $scope.isValidating = false;
  $scope.countThreemaRecordsNotFoundInENT = 0;
  $scope.countENTRecordsNotFoundInThreema = 0;
  $scope.countSuggestionsForNameChange = 0;

  $scope.sorts = [
    { name: "Class", fx: (c) => _getClassLevel(c.cls) },
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

  function validate() {
    $scope.isValidating = true;
    $http
      .post("/api/threema_connector/credentials/check", {
        idsToCheck: null,
      })
      .then((resp) => {
        $scope.validated = true;
        const { ok, suggestions, unmatched, unused } = resp.data;
        const ok_ids = ok.map((c) => c.id);
        const unmatched_ids = unmatched.map((c) => c.id);
        const suggestions_ids = suggestions.map((c) => c.id);

        $scope.countENTRecordsNotFoundInThreema = unused.length;
        $scope.countThreemaRecordsNotFoundInENT = unmatched_ids.length;
        $scope.countSuggestionsForNameChange = suggestions_ids.length;

        for (let cred of $scope.credentials) {
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

        if (unmatched_ids.length + suggestions_ids.length + unused.length === 0) {
          notify.success("Threema and ENT are perfectly synced. Nothing to do here.");
        } else {
          notify.success("Data deviations between Threema and ENT have been found. Check the options below the list to adjust.");
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
        validate();
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
        allUsers: () => false,
      },
    });

    modal.result.then(() => {
      notify.success(gettext("Deleted"));
      $scope.credentials = $scope.credentials.filter((c) => c.id !== threemaId);
    });
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

  const classToLevel = {
    "5a": 5,
    "5b": 5,
    "6a": 6,
    "6b": 6,
    "7a": 7,
    "7b": 7,
    "8a": 8,
    "8b": 8,
    "9a": 9,
    "9b": 9,
    "6I": 6,
    "6II": 6,
    "5I": 7,
    "5II": 7,
    "4I": 8,
    "4II": 8,
    "3I": 9,
    "3II": 9,
    "2L1": 10,
    "2L2": 10,
    "2ES": 10,
    "2S1": 10,
    "2S2": 10,
    "1L1": 11,
    "1L2": 11,
    "1ES": 11,
    "1SMP": 11,
    "1SBC1": 11,
    "1SBC2": 11,
    TL1: 12,
    TL2: 12,
    TES: 12,
    TSMP: 12,
    TSBC1: 12,
    TSBC2: 12,
  };

  function _getClass(username) {
    for (let [name] of Object.entries(classToLevel)) {
      if (username.startsWith(name + "_")) {
        return name;
      }
    }
    return "?";
  }

  function _getClassLevel(c) {
    return classToLevel[c] || -1;
  }
});
