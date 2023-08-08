angular.module("dfglfa.threema_connector").controller("ThreemaPasswordsController", function ($scope, $http, pageTitle, gettext, notify, $uibModal) {
  $scope.classesForLevel = {
    5: ["5a", "5b"],
    6: ["6a", "6b", "6I", "6II"],
    7: ["7a", "7b", "5I", "5II"],
    8: ["8a", "8b", "4I", "4II"],
    9: ["9a", "9b", "3I", "3II"],
    10: ["2L1", "2L2", "2ES", "2S1", "2S2"],
    11: ["1L1", "1L2", "1ES", "1SMP", "1SBC1", "1SBC2"],
    12: ["TL1", "TL2", "TES", "TSMP", "TSBC1", "TSBC2"],
  };

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
