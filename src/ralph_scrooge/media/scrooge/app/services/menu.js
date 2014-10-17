var scrooge = angular.module('scrooge.services', ['ngResource']);

scrooge.factory('MainMenu', ['$resource', function ($resource) {
    return {
        'items': $resource('/scrooge/rest/menu', {}, {
            get: {
                method: 'GET',
                cache: true,
                isArray: true,
            }
        })
    }
}]);
