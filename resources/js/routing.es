angular.module('example.threema_connector').config(($routeProvider) => {
    $routeProvider.when('/view/threema_connector', {
        templateUrl: '/threema_connector:resources/partial/index.html',
        controller: 'ThreemaConnectorIndexController',
    });
});
