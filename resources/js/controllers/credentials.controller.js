angular
  .module("dfglfa.threema_connector")
  .controller("CredentialsController", function ($scope, $http, pageTitle, gettext, notify, $uibModal, classService) {
    pageTitle.set(gettext("Threema"));

    $scope.reverse = false;

    $scope.entMatchInProgress = false;
    $scope.validated = false;
    $scope.countThreemaRecordsNotFoundInENT = 0;
    $scope.countENTRecordsNotFoundInThreema = 0;
    $scope.countSuggestionsForNameChange = 0;

    $scope.sorts = [
      { name: "Class", fx: (c) => classService.getClassLevel(c.cls) },
      { name: "Name", fx: (c) => c.username },
      { name: "Validation", fx: (c) => validationLevel(c.status) },
      { name: "Active", fx: (c) => c.usage },
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

    $scope.validate = validate;
    $scope.openCredentialsChangeModal = openCredentialsChangeModal;
    $scope.openCredentialsDeleteModal = openCredentialsDeleteModal;

    loadCredentials();

    function loadCredentials() {
      $scope.entMatchInProgress = true;
      $http.get("/api/threema_connector/credentials").then((resp) => {
        $scope.credentials = resp.data;
        validate();
      });
    }

    function validate() {
      $scope.entMatchInProgress = true;
      $http
        .post("/api/threema_connector/credentials/check", {
          idsToCheck: null,
        })
        .then((resp) => {
          $scope.validated = true;
          const { matched, unmatched, unused } = resp.data;
          const unmatched_ids = unmatched.map((c) => c.id);

          // Dictionary that contains data for all cred ids for which a match has been found
          // This might not be an exact match and still need a slight correction.
          const matchedDataForCredsId = {};
          for (let m of matched) {
            matchedDataForCredsId[m.credsId] = m;
          }

          $scope.countENTRecordsNotFoundInThreema = unused.length;
          $scope.countThreemaRecordsNotFoundInENT = unmatched_ids.length;

          let changeCount = 0;
          for (let cred of $scope.credentials) {
            let entMatch = matchedDataForCredsId[cred.id];
            if (entMatch) {
              cred.cls = entMatch["cls"];
              if (entMatch["currentThreemaLogin"] === entMatch["correctThreemaLogin"]) {
                cred.status = "OK";
              } else {
                cred.status = "SUGGESTION";
                cred.nameChange = entMatch["correctThreemaLogin"];
                changeCount++;
              }
            } else if (unmatched_ids.indexOf(cred.id) > -1) {
              cred.status = "UNMATCHED";
            } else {
              cred.status = "UNKNOWN";
            }
          }

          $scope.countSuggestionsForNameChange = changeCount;

          if (unmatched_ids.length + unused.length + changeCount === 0) {
            notify.success("Threema and ENT are perfectly synced. Nothing to do here.");
          } else {
            notify.success("Data deviations between Threema and ENT have been found.");
          }
        })
        .finally(() => ($scope.entMatchInProgress = false));
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
          cred.cls = classService.getClass(newName);
          $scope.validated && validate();
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
  });
