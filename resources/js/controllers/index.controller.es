angular.module('example.threema_connector').controller('ThreemaConnectorIndexController', function($scope, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('ThreemaConnector'));

    $scope.counter = 0;

    $scope.click = () => {
            $scope.counter += 1;
            notify.info('+1');
        };

    // Bind a test var with the template.
    $scope.my_title = gettext('ThreemaConnector');
    
    // GET a result through Python API
    $http.get('/api/threema_connector').then( (resp) => {
	    $scope.python_get = resp.data;
    });

    // POST a result through Python API
    $http.post('/api/threema_connector', {my_var: 'threema_connector'}).then( (resp) => {
	    $scope.python_post = resp.data;
    });

});

