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
            if (stats.currentSubMenu.auto_choose_env) {
                var envExist = false;
                service.value.envs.forEach(function(element) {
                    if (element.env == stats.menuStats['env']['current']) {
                        envExist = true;
                    }
                });
                if (envExist === false) {
                    stats.menuStats['env']['change'] = service.value.envs[0].id;
                }
            } else {
                stats.menuStats['env']['change'] = false;
            }
            stats.refreshData();
        },
        changeEnv: function(env) {
            stats.menuStats['env']['change'] = env;
            stats.refreshData();
        },
    };
}]);
