angular.module("dfglfa.threema_connector").controller("NormalizationsController", function ($scope, $http, pageTitle, gettext, notify) {
  pageTitle.set(gettext("Contacts"));

  $scope.isUpdating = false;

  $scope.changes = undefined;
  $scope.missing = undefined;
  $scope.apply = applyChange;
  $scope.create = create;
  loadNormalizations();

  function loadNormalizations() {
    return $http.get("/api/threema_connector/normalizations", {}).then(({ data: { updates, missing } }) => {
      $scope.changes = updates;
      $scope.missing = missing;
    });
  }

  function applyChange(change) {
    $scope.isUpdating = true;
    return $http
      .post("/api/threema_connector/normalize", {
        threemaId: change.threemaId,
        firstName: change.firstNameNormalized,
        lastName: change.lastNameNormalized,
        enabled: change.enabled,
      })
      .then(() => {
        notify.success("Change applied");
        for (const c of $scope.changes) {
          if (c.threemaId === change.threemaId) {
            c.done = true;
          }
        }
      })
      .finally(() => {
        $scope.isUpdating = false;
      });
  }

  function create(contact) {
    $scope.isUpdating = true;
    return $http
      .post("/api/threema_connector/contacts", {
        threemaId: contact.threemaId,
        firstName: contact.firstName,
        lastName: contact.lastName,
      })
      .then(() => {
        notify.success("Contact created");
        for (const n of $scope.missing) {
          if (n.threemaId === contact.threemaId) {
            n.done = true;
          }
        }
      })
      .finally(() => {
        $scope.isUpdating = false;
      });
  }
});
