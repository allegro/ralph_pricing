'use strict';

var scrooge = angular.module('scrooge.service.menu', ['ngResource']);

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

scrooge.factory('menuService', ['stats', function (stats) {
    return {
        changeService: function(service) {
            stats.menuStats['service']['change'] = service.id;
            stats.menuStats['env']['change'] = false;
            stats.refreshData();
        },
        changeEnv: function(env) {
            stats.menuStats['env']['change'] = env;
            stats.refreshData();
        },
    };
}]);
