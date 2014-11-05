'use strict';

var scrooge = angular.module('scrooge.services', ['ngResource']);

scrooge.factory('SubMenu', ['$resource', function ($resource) {
    return {
        'items': $resource('/scrooge/rest/submenu', {}, {
            get: {
                method: 'GET',
                cache: true,
                isArray: true,
            }
        })
    };
}]);
