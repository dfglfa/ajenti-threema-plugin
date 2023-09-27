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
