angular.module("dfglfa.threema_connector").controller("NormalizationsController", function ($scope, $http, pageTitle, gettext, notify) {
  pageTitle.set(gettext("Contacts"));

  $scope.isUpdating = false;

  $scope.changes = undefined;
  $scope.apply = applyChange;
  loadNormalizations();

  function loadNormalizations() {
    return $http.get("/api/threema_connector/normalizations", {}).then(({ data: changes }) => {
      $scope.changes = changes;
    });
  }

  function applyChange(change) {
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
      });
  }
});
