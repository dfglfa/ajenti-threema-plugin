// the module should depend on 'core' to use the stock services & components
angular.module("dfglfa.threema_connector", ["core"]);

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

angular.module("dfglfa.threema_connector").controller("ThreemaConnectorIndexController", function ($scope, $http, $location, classService) {
  let queryParams = $location.search();
  $scope.activetab = +queryParams.active || 0;

  loadCredentials();

  function loadCredentials() {
    $http.get("/api/threema_connector/credentials").then((resp) => {
      sortByUserType(resp.data);
    });
  }

  function sortByUserType(credentials) {
    const studentsCreds = [];
    const teachersCreds = [];

    for (let c of credentials) {
      if (c.username && classService.getClass(c.username)) {
        studentsCreds.push(c);
      } else {
        // Teachers have no class :o)
        teachersCreds.push(c);
      }
    }

    $scope.studentsCredentials = studentsCreds;
    $scope.teachersCredentials = teachersCreds;
    $scope.credentials = credentials;
  }

  $scope.onCredsChange = () => {
    sortByUserType($scope.studentsCredentials.concat($scope.teachersCredentials));
  };
});

angular
  .module("dfglfa.threema_connector")
  .controller("MissingController", function ($scope, $http, $timeout, pageTitle, gettext, notify) {
    pageTitle.set(gettext("Missing"));

    $scope.isUpdating = false;
    $scope.add = addCredentials;
    $scope.addSelectedCredentials = addSelectedCredentials;
    $scope.toggle = toggle;
    $scope.selectAll = selectAll;
    $scope.unselectAll = unselectAll;

    // Check on page load
    $scope.results = undefined;
    loadResults();

    $scope.queue = [];
    $scope.done = 0;
    $scope.total = 0;
    $scope.selectedNames = [];
    $scope.allNames = [];

    $scope.THREEMA_PREFIX = "dfg";

    function loadResults() {
      return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
        $scope.results = resp.data.unused;
        $scope.selectedNames = $scope.results;
        $scope.allNames = $scope.results;
      });
    }

    function toggle(uid) {
      if ($scope.selectedNames.indexOf(uid) === -1) {
        $scope.selectedNames.push(uid);
      } else {
        $scope.selectedNames = $scope.selectedNames.filter(i => i !== uid);
      }
    }

    function addCredentials(entLogin, singleUpdate) {
      if (singleUpdate) {
        $scope.isUpdating = true;
      }

      const threemaUsername = $scope.THREEMA_PREFIX + "_" + entLogin;

      return $http
        .put("/api/threema_connector/credentials", { username: threemaUsername })
        .then(() => {
          notify.success(`User ${threemaUsername} successfully created`);
          singleUpdate && loadResults();
        })
        .finally(() => {
          if (singleUpdate) {
            $scope.isUpdating = false;
          }
        });
    }

    function addSelectedCredentials() {
      const allTasks = [];
      for (let uname of $scope.results) {
        if ($scope.selectedNames.indexOf(uname) > -1) {
          allTasks.push(uname);
        }
      }

      $scope.isUpdating = true;
      $scope.queue = allTasks;
      $scope.total = allTasks.length;
      $scope.done = 0;
      processQueue();
    }

    function processQueue() {
      if ($scope.queue.length === 0) {
        $timeout(() => {
          $scope.total = 0;
          $scope.done = 0;
          $scope.isUpdating = false;
          loadResults();
        }, 500);
      } else {
        const newName = $scope.queue.pop();
        addCredentials(newName).then(() => {
          $scope.done++;
          $timeout(processQueue, 300);
        });
      }
    }

    function selectAll() {
      $scope.selectedNames = $scope.allNames;
    }

    function unselectAll() {
      $scope.selectedNames = [];
    }
  });

angular.module("dfglfa.threema_connector").controller("UnmatchedController", function ($scope, $http, $uibModal, $timeout, notify, classService) {
  $scope.isUpdating = false;
  $scope.delete = deleteCredentials;
  $scope.deleteSelected = deleteSelectedCredentials;
  $scope.openCredentialsDeleteModal = openCredentialsDeleteModal;
  $scope.toggle = toggle;
  $scope.selectAll = selectAll;
  $scope.unselectAll = unselectAll;

  // Check on page load
  $scope.unmatchedCredentials = undefined;
  loadResults();

  $scope.queue = [];
  $scope.done = 0;
  $scope.total = 0;
  $scope.selectedIds = [];
  $scope.allIds = [];

  function loadResults() {
    return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
      const unmatchedCredentials = [];
      for (const user of resp.data.unmatched) {
        unmatchedCredentials.push(user);
      }
      $scope.unmatchedCredentials = unmatchedCredentials;
      $scope.selectedIds = unmatchedCredentials.map(c => c.id);
      $scope.allIds = $scope.selectedIds;
    });
  }

  function toggle(uid) {
    if ($scope.selectedIds.indexOf(uid) === -1) {
      $scope.selectedIds.push(uid);
    } else {
      $scope.selectedIds = $scope.selectedIds.filter(i => i !== uid);
    }
  }

  function deleteCredentials(threemaId, username, singleDelete) {
    if (singleDelete) {
      $scope.isUpdating = true;
    }

    return $http
      .delete("/api/threema_connector/credentials/" + threemaId)
      .then(() => {
        notify.success(`Threema user ${username} successfully deleted`);
        singleDelete && loadResults();
      })
      .finally(() => {
        if (singleDelete) {
          $scope.isUpdating = false;
        }
      });
  }

  function openCredentialsDeleteModal() {
    const modal = $uibModal.open({
      templateUrl: "/threema_connector:resources/partial/credentialsDelete.modal.html",
      controller: "CredentialsDeleteController",
      size: "lg",
      resolve: {
        threemaId: () => undefined,
        username: () => undefined,
        multipleUsers: () => true,
      },
    });

    modal.result.then(deleteSelectedCredentials);
  }

  function deleteSelectedCredentials() {
    const allTasks = [];
    for (let unmatched of $scope.unmatchedCredentials) {
      if ($scope.selectedIds.indexOf(unmatched.id) > -1) {
        allTasks.push([unmatched.id, unmatched.username]);
      }
    }

    $scope.isUpdating = true;
    $scope.queue = allTasks;
    $scope.total = allTasks.length;
    $scope.done = 0;
    $timeout(processQueue, 1000);
  }

  function processQueue() {
    if ($scope.queue.length === 0) {
      $timeout(() => {
        $scope.total = 0;
        $scope.done = 0;
        $scope.isUpdating = false;
        loadResults();
      }, 500);
    } else {
      const [threemaId, username] = $scope.queue.pop();
      deleteCredentials(threemaId, username).then(() => {
        $scope.done++;
        $timeout(processQueue, 500);
      });
    }
  }

  function selectAll() {
    $scope.selectedIds = $scope.allIds;
  }

  function unselectAll() {
    $scope.selectedIds = [];
  }
});

angular.module("dfglfa.threema_connector").controller("SuggestionsController", function ($scope, $http, $timeout, notify) {
  $scope.isUpdating = false;
  $scope.apply = applySuggestion;
  $scope.applyAll = applyAllSuggestions;

  $scope.queue = [];
  $scope.done = 0;
  $scope.total = 0;

  // Check on page load
  $scope.results = undefined;
  loadResults();

  function loadResults() {
    return $http.post("/api/threema_connector/credentials/check", {}).then((resp) => {
      let suggestions = [];
      for (let entry of resp.data.matched) {
        if (entry.currentThreemaLogin !== entry.correctThreemaLogin) {
          suggestions.push(entry);
        }
      }
      $scope.suggestions = suggestions;
      console.log("Suggestions: ", $scope.suggestions);
    });
  }

  function applySuggestion(threemaId, newName, singleUpdate) {
    if (singleUpdate) {
      $scope.isUpdating = true;
    }

    return $http
      .post("/api/threema_connector/credentials/update", {
        threemaId,
        changedName: newName,
      })
      .then(() => {
        notify.success(`User successfully renamed to ${newName}`);
        singleUpdate && loadResults();
      })
      .catch(() => {
        notify.error(`Error renaming user to ${newName}`);
      })
      .finally(() => {
        if (singleUpdate) {
          $scope.isUpdating = false;
        }
      });
  }

  function applyAllSuggestions() {
    const allTasks = [];
    for (let suggestion of $scope.suggestions) {
      allTasks.push([suggestion.credsId, suggestion.correctThreemaLogin]);
    }

    $scope.isUpdating = true;
    $scope.queue = allTasks;
    $scope.total = allTasks.length;
    $scope.done = 0;
    $timeout(processQueue, 1000);
  }

  function processQueue() {
    if ($scope.queue.length === 0) {
      $timeout(() => {
        $scope.total = 0;
        $scope.done = 0;
        $scope.isUpdating = false;
        loadResults();
      }, 500);
    } else {
      const [threemaId, newName] = $scope.queue.pop();
      applySuggestion(threemaId, newName).then(() => {
        $scope.done++;
        $timeout(processQueue, 500);
      });
    }
  }
});

angular
  .module("dfglfa.threema_connector")
  .controller("CredentialsChangeController", function ($scope, $http, $uibModalInstance, threemaId, oldName, newName) {
    $scope.data = { oldName, newName, password: "" };
    $scope.error = undefined;
    $scope.isUpdating = false;

    $scope.save = () => {
      $scope.isUpdating = true;
      $http
        .post("/api/threema_connector/credentials/update", {
          threemaId,
          changedName: $scope.data.newName,
          changedPassword: $scope.data.password,
        })
        .then(() => {
          $scope.isUpdating = false;
          $uibModalInstance.close($scope.data.newName);
        })
        .catch((err) => {
          $scope.isUpdating = false;
          $scope.error = err;
        });
    };

    $scope.cancel = () => {
      $uibModalInstance.dismiss();
    };
  });

angular
  .module("dfglfa.threema_connector")
  .controller("CredentialsDeleteController", function ($scope, $http, $uibModalInstance, threemaId, username, multipleUsers) {
    $scope.username = username;
    $scope.isDeleting = false;
    $scope.multipleUsers = multipleUsers;

    $scope.delete = () => {
      if (!multipleUsers) {
        $scope.isDeleting = true;

        $http
          .delete("/api/threema_connector/credentials/" + threemaId)
          .then(() => {
            $scope.isDeleting = false;
            $uibModalInstance.close();
          })
          .catch((err) => {
            $scope.isDeleting = false;
            $scope.error = err;
          });
      } else {
        $uibModalInstance.close();
      }
    };

    $scope.cancel = () => {
      $uibModalInstance.dismiss();
    };
  });

angular
  .module("dfglfa.threema_connector")
  .controller("CredentialsController", function ($scope, $http, pageTitle, gettext, notify, $uibModal, classService) {
    pageTitle.set(gettext("Threema"));

    $scope.reverse = false;

    $scope.entMatchInProgress = false;
    $scope.validated = false;
    $scope.countThreemaCredsNotFoundInLdap = 0;
    $scope.countLdapUsersNotFoundInThreema = 0;
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
      $http.get("/api/threema_connector/credentials").then((resp) => {
        $scope.credentials = resp.data;
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

          $scope.countLdapUsersNotFoundInThreema = unused.length;
          $scope.countThreemaCredsNotFoundInLdap = unmatched_ids.length;

          let changeCount = 0;
          for (let cred of $scope.credentials) {
            let entMatch = matchedDataForCredsId[cred.id];
            if (entMatch) {
              cred.cls = entMatch["cls"];
              if (entMatch["currentThreemaLogin"] === entMatch["correctThreemaLogin"]) {
                cred.status = "OK";
                cred.realname = `${entMatch.lastName}, ${entMatch.firstName}`;
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
            notify.success("Threema and LDAP are perfectly synced. Nothing to do here.");
          } else {
            notify.success("Data deviations between Threema and LDAP have been found.");
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
          multipleUsers: () => false,
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

angular.module("dfglfa.threema_connector").controller("ThreemaGroupsController", function ($scope, $http) {
  loadDataForAllGroups();
  $scope.groups = undefined;

  function loadDataForAllGroups() {
    return $http.get("/api/threema_connector/groups").then(({ data: groups }) => {
      $scope.groups = groups;
    });
  }
});

angular
  .module("dfglfa.threema_connector")
  .controller("ThreemaGroupCreationController", function ($scope, $http, $timeout, $location, $uibModal, notify) {
    $scope.groupId = $location.search().id;
    $scope.groupName = undefined;
    $scope.existingMembers = undefined;
    $scope.newMembers = [];
    $scope.searching = false;
    $scope.maxResults = 30;

    $scope.searchContacts = searchContacts;
    $scope.createGroup = createGroup;
    $scope.updateGroupMembers = updateGroupMembers;
    $scope.addResults = addResults;
    $scope.loadMembers = loadMembers;
    $scope.addNewMember = addNewMember;
    $scope.removeNewMember = removeNewMember;
    $scope.removeFromGroup = removeFromGroup;
    $scope.processCSVFile = processCSVFile;
    $scope.openCSVUploadDialog = openCSVUploadDialog;
    $scope.addAllFromClass = addSyncForClass;

    let debounceTimer;
    function searchContacts() {
      if (debounceTimer) {
        $timeout.cancel(debounceTimer);
      }

      debounceTimer = $timeout(runSearch, 500);
    }

    if ($scope.groupId) {
      loadMembers();
      loadGroupInfo();
    } else {
      $scope.groupName = "";
      $scope.existingMembers = [];
    }

    function runSearch() {
      if (!$scope.search || $scope.search.length < 2) {
        $scope.results = [];
        return;
      }

      const searchTerm = $scope.search.toLowerCase();

      $scope.searching = true;
      return $http
        .get("/api/threema_connector/contacts", {})
        .then(({ data: contacts }) => {
          const results = [];
          const alreadyListed = $scope.existingMembers.concat($scope.newMembers).map((m) => m.id);
          for (const c of contacts) {
            if (!c.enabled || alreadyListed.indexOf(c.id) !== -1) {
              continue;
            }

            const searchtarget = `${c.firstName ? c.firstName.toLowerCase() : ""} ${
              c.lastName ? c.lastName.toLowerCase() : ""
            } ${c.id.toLowerCase()}`;
            if (searchtarget.indexOf(searchTerm) > -1) {
              results.push(c);
            }
          }

          $scope.results = results;
        })
        .finally(() => {
          $scope.searching = false;
        });
    }

    function addResults() {
      const members = [];
      const alreadyAdded = $scope.newMembers.map((m) => m.id);
      const existingIds = $scope.existingMembers.map((m) => m.id);
      for (const r of $scope.results) {
        if (alreadyAdded.indexOf(r.id) === -1 && existingIds.indexOf(r.id) === -1) {
          members.push(r);
        }
      }
      $scope.newMembers = $scope.newMembers.concat(members);
      runSearch();
    }

    function createGroup() {
      return $http.post("/api/threema_connector/groups", { name: $scope.groupName, members: $scope.newMembers.map((m) => m.id) }).then(() => {
        $location.url("/view/threema_connector?active=3");
        console.log("Group successfully created");
      });
    }

    function updateGroupMembers() {
      console.log("Updating id", $scope.groupId);
      return $http.post("/api/threema_connector/group_members", { groupId: $scope.groupId, members: $scope.newMembers.map((m) => m.id) }).then(() => {
        const existingMembers = $scope.existingMembers;
        for (const m of $scope.newMembers) {
          existingMembers.push(m);
        }
        $scope.newMembers = [];
        $scope.existingMembers = existingMembers;
      });
    }

    function loadMembers() {
      return $http.get(`/api/threema_connector/group_members`, { params: { groupId: $scope.groupId } }).then(({ data: members }) => {
        const mems = [];
        for (const m of members) {
          mems.push({ id: m.id, firstName: m.firstName, lastName: m.lastName });
        }
        $scope.existingMembers = mems;
      });
    }

    function addNewMember(m) {
      $scope.newMembers.push(m);
      $scope.results = $scope.results.filter((r) => r.id !== m.id);
    }

    function removeNewMember(m) {
      $scope.newMembers = $scope.newMembers.filter((nm) => nm.id !== m.id);
      runSearch();
    }

    function openCSVUploadDialog() {
      const modal = $uibModal.open({
        templateUrl: "/threema_connector:resources/partial/csvUpload.modal.html",
        controller: "CSVUploadController",
        size: "md",
      });

      modal.result.then(({ file }) => {
        processCSVFile(file);
      });
    }

    function processCSVFile(file) {
      if (file) {
        var reader = new FileReader();

        // Define a callback for when the file is loaded
        reader.onload = function (e) {
          var fileContents = e.target.result;
          $http.post(`/api/threema_connector/group_members/csv`, { data: fileContents }).then(({ data: { added, notFound } }) => {
            $scope.newMembers = added;
            console.log("Not found:", notFound);
            if (notFound && notFound.length > 0) {
              notify.warning(notFound.length + " users from the csv could not be found among the active contacts");
            } else {
              notify.success("All users from the csv have been found.");
            }
          });
        };

        reader.readAsText(file);
      } else {
        notify.info("No file selected.");
      }
    }

    function removeFromGroup(memberId) {
      return $http.post(`/api/threema_connector/remove_group_members`, { groupId: $scope.groupId, memberIds: [memberId] }).then(() => {
        console.log("Deleted ", memberId);
        $scope.existingMembers = $scope.existingMembers.filter((m) => m.id !== memberId);
      });
    }

    function loadGroupInfo() {
      return $http.get(`/api/threema_connector/group_details`, { params: { groupId: $scope.groupId } }).then(({ data }) => {
        $scope.groupName = data.name;
      });
    }

    function addSyncForClass() {
      return $http
        .get(`/api/threema_connector/group_sync`, { params: { groupId: $scope.groupId, className: $scope.selectedClass } })
        .then(({ data }) => {
          notify.info("Group sync succesfully created.");
          console.log("Sync creation response:", data);
        });
    }
  });

angular.module("dfglfa.threema_connector").controller("ThreemaPasswordsController", function ($scope, $http, classService) {
  $scope.selectedGroup = undefined;
  $scope.selectGroup = selectGroup;
  $scope.toggleVisibility = toggleVisibility;
  $scope.downloadPasswordList = downloadPasswordList;

  $scope.classesForLevel = {
    5: ["5a", "5b"],
    6: ["6a", "6b", "6eI", "6eII"],
    7: ["7a", "7b", "5eI", "5eII"],
    8: ["8a", "8b", "4eI", "4eII"],
    9: ["9a", "9b", "3eI", "3eII"],
    10: ["2L1", "2L2", "2ES", "2S1", "2S2"],
    11: ["1L1", "1L2", "1ES", "1SMP", "1SBC1", "1SBC2"],
    12: ["TL1", "TL2", "TES", "TSMP", "TSBC1", "TSBC2"],
  };

  function selectGroup(group) {
    if (group) {
      $scope.selectedGroup = group;
      loadStudentsDataForSelectedGroup();
    } else {
      $scope.selectedGroup = undefined;
    }
  }

  function loadStudentsDataForSelectedGroup() {
    $scope.students = undefined;
    return $http.get("/api/threema_connector/credentials_with_passwords", { params: { classname: $scope.selectedGroup } }).then((resp) => {
      $scope.students = resp.data;
      $scope.activeMembers = $scope.students.filter((s) => s.usage > 0);
    });
  }

  function createAndDownloadTextFile(textContent, filename) {
    const blob = new Blob([textContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function downloadPasswordList() {
    let content = "Benutzername,Passwort\n";
    $scope.students.forEach((s) => {
      content += `${s.username},${s.password}\n`;
    });
    createAndDownloadTextFile(content, `passwords_${$scope.selectedGroup}.csv`);
  }

  function toggleVisibility(studentId) {
    $scope.students.forEach((s) => {
      if (s.id === studentId) {
        s.showPassword = !s.showPassword;
      }
    });
  }
});

angular.module("dfglfa.threema_connector").controller("ContactsController", function ($scope, $http, pageTitle, gettext, notify) {
  pageTitle.set(gettext("Contacts"));

  $scope.isUpdating = false;

  $scope.sorts = [
    { name: "First name", fx: (c) => c.firstName },
    { name: "Last name", fx: (c) => c.lastName },
    { name: "Enabled", fx: (c) => c.enabled },
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

  // Check on page load
  $scope.contacts = undefined;
  loadResults().then(matchUsers);

  function loadResults() {
    return $http.get("/api/threema_connector/contacts", {}).then(({ data: contacts }) => {
      $scope.contacts = contacts;
    });
  }

  function matchUsers() {
    return $http.get("/api/threema_connector/users", {}).then(({ data: users }) => {
      const userDict = {};
      for (const u of users) {
        userDict[u.id] = u;
      }

      for (const c of $scope.contacts) {
        if (userDict[c.id]) {
          c.matchingUsername = userDict[c.id].nickname;
        }
      }
    });
  }
});

angular.module("dfglfa.threema_connector").controller("ThreemaUsersController", function ($scope, $http, $uibModal, gettext, notify) {
  $scope.users = undefined;
  $scope.paging = { pageSize: 50, page: 1 };

  $scope.orphans = [];
  $scope.openUserDeleteModal = openUserDeleteModal;

  const credentials_dict = {};
  loadCredentials().then(loadUsers);

  function loadCredentials() {
    return $http.get("/api/threema_connector/credentials").then((resp) => {
      for (const cred of resp.data) {
        credentials_dict[cred.id] = cred;
      }
      console.log("Dict:", credentials_dict);
    });
  }

  function loadUsers() {
    return $http.get("/api/threema_connector/users").then((resp) => {
      //const userdata = resp.data.concat({ id: 123, nickname: "hans", lastCheck: "2023-09-10" });
      const userdata = resp.data;

      const usage = {};
      for (const u of userdata) {
        if (usage[u.credentials_id]) {
          usage[u.credentials_id]++;
        } else {
          usage[u.credentials_id] = 1;
        }
      }

      const user_list = [];
      const orphans = [];
      for (const u of userdata) {
        creds_usage = usage[u.credentials_id];
        creds_id = credentials_dict[u.credentials_id];
        deletable = !creds_id || (creds_usage > 1 && getDaysPast(u.lastCheck) > 90);
        console.log("Last login of " + u.nickname + " was " + getDaysPast(u.lastCheck) + " days ago: " + u.lastCheck);

        if (!creds_id) {
          orphans.push(u);
        }

        user_list.push({
          ...u,
          credentials_name: creds_id?.username,
          usage: creds_usage,
          deletable,
        });
      }

      $scope.users = user_list;
      $scope.orphans = orphans;
    });
  }

  function openUserDeleteModal(users) {
    const modal = $uibModal.open({
      templateUrl: "/threema_connector:resources/partial/userDelete.modal.html",
      controller: "UserDeleteController",
      size: "lg",
      resolve: {
        users: () => users,
      },
    });

    modal.result.then(() => {
      const userIds = users.map((u) => u.id);
      notify.success(gettext("Deleted"));
      $scope.users = $scope.users.filter((c) => userIds.indexOf(c.id) === -1);
      $scope.orphans = $scope.orphans.filter((o) => userIds.indexOf(o.id) === -1);
    });
  }

  function getDaysPast(targetDate) {
    const currentDate = new Date();
    const timeDifference = currentDate - new Date(targetDate);
    const daysDifference = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
    return daysDifference;
  }
});

angular.module("dfglfa.threema_connector").controller("UserDeleteController", function ($scope, $http, $uibModalInstance, $timeout, users) {
  $scope.users = users;
  $scope.isDeleting = false;

  $scope.deleteUsers = deleteUsers;

  $scope.cancel = () => {
    $uibModalInstance.dismiss();
  };

  const idList = users.map((u) => u.id);

  function deleteUsers() {
    if (idList.length === 0) {
      $scope.isDeleting = false;
      $uibModalInstance.close();
      return;
    }

    $scope.isDeleting = true;
    const userId = idList.pop();
    deleteUser(userId).then(() => {
      $timeout(deleteUsers, 300);
    });
  }

  function deleteUser(userId) {
    return $http
      .delete("/api/threema_connector/users/" + userId)
      .then(() => {
        $uibModalInstance.close();
      })
      .catch((err) => {
        $scope.isDeleting = false;
        $scope.error = err;
      });
  }
});

angular.module("dfglfa.threema_connector").controller("NormalizationsController", function ($scope, $http, pageTitle, gettext, notify) {
  pageTitle.set(gettext("Contacts"));

  $scope.isUpdating = false;

  $scope.changes = undefined;
  $scope.missing = undefined;
  $scope.no_ent_match = undefined;

  $scope.apply = applyChange;
  $scope.create = create;
  loadNormalizations();

  function loadNormalizations() {
    return $http.get("/api/threema_connector/normalizations", {}).then(({ data: { updates, missing, no_ent_match } }) => {
      $scope.changes = updates;
      $scope.missing = missing;
      $scope.no_ent_match = no_ent_match;
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

angular.module("dfglfa.threema_connector").controller("CSVUploadController", function ($scope, $uibModalInstance) {
  $scope.processFile = () => {
    var fileInput = document.getElementById("fileInput");
    var file = fileInput.files[0];
    console.log("Reading file", file);
    $uibModalInstance.close({ file });
  };

  $scope.cancel = () => {
    $uibModalInstance.dismiss();
  };
});

angular.module("dfglfa.threema_connector").directive("credentials", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/credentials.html",
    controller: "CredentialsController",
  };
});

angular.module("dfglfa.threema_connector").directive("groups", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/groups.html",
    controller: "ThreemaGroupsController",
  };
});

angular.module("dfglfa.threema_connector").directive("passwords", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/passwords.html",
    controller: "ThreemaPasswordsController",
  };
});

angular.module("dfglfa.threema_connector").directive("contacts", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/contacts.html",
    controller: "ContactsController",
  };
});

angular.module("dfglfa.threema_connector").directive("users", function () {
  return {
    restrict: "E",
    templateUrl: "/threema_connector:resources/partial/users.html",
    controller: "ThreemaUsersController",
  };
});

angular.module("dfglfa.threema_connector").service("classService", function () {
  const api = this;
  api.getClass = _getClass;
  api.getClassLevel = _getClassLevel;
  api.containsClass = _containsClass;
  api.getClassNames = _getClassNames;

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
    "6eI": 6,
    "6eII": 6,
    "5eI": 7,
    "5eII": 7,
    "4eI": 8,
    "4eII": 8,
    "3eI": 9,
    "3eII": 9,
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
    Lehrer: 100,
  };

  const incorrectClassnames = ["6I", "6II", "5I", "5II", "4I", "4II", "3I", "3II"];

  function _getClass(username) {
    if (!username) {
      return null;
    }

    for (let [name] of Object.entries(classToLevel)) {
      if (username.startsWith(name + "_")) {
        return name;
      }
    }

    return null;
  }

  function _containsClass(username) {
    if (!username) {
      return false;
    }

    for (let [name] of Object.entries(classToLevel)) {
      if (username.startsWith(name)) {
        return true;
      }
    }

    // backwards compat for initial migration
    for (let name of incorrectClassnames) {
      if (username.startsWith(name)) {
        return true;
      }
    }

    return false;
  }

  function _getClassLevel(c) {
    return classToLevel[c] || -1;
  }

  function _getClassNames() {
    return Object.keys(classToLevel);
  }
});

