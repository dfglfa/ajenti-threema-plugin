angular
  .module("example.threema_connector")
  .controller("ThreemaConnectorConcistencyController", function ($scope, $http, $uibModal, pageTitle, gettext, notify) {
    pageTitle.set(gettext("Consistency"));

    $scope.isUpdating = false;
    $scope.add = addCredentials;
    $scope.addAll = addCredentialsForAll;
    $scope.delete = openCredentialsDeleteModal;

    // Check on page load
    $scope.results = undefined;
    check();

    function check() {
      return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
        $scope.results = resp.data;
      });
    }

    function addCredentials(username, doCheck) {
      $scope.isUpdating = true;
      return $http
        .put("/api/threema_connector/credentials", { username })
        .then(() => {
          notify.success(`User ${username} successfully created`);
          doCheck && check();
        })
        .finally(() => ($scope.isUpdating = false));
    }

    function addCredentialsForAll() {
      const allTasks = [];
      for (let uname of $scope.results.unused) {
        allTasks.push(addCredentials(uname));
      }
      Promise.all(allTasks).then(() => {
        notify.success("All credentials created");
        check();
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
        $scope.results.unmatched = $scope.results.unmatched.filter((c) => c.id !== threemaId);
      });
    }
  });
