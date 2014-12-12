'use strict';

var scrooge = angular.module('scrooge.filter', []);

scrooge.filter('breadcrumbs', ['stats', function(stats) {
    return function(input, scope) {
        switch(scope) {
            case 'env':
                for (var i in stats.leftMenus[stats.currentLeftMenu]) {
                    for (var k in stats.leftMenus[stats.menuStats.leftMenu][i].value.envs) {
                        if (stats.leftMenus[stats.menuStats.leftMenu][i].value.envs[k].id == input) {
                            return stats.leftMenus[stats.menuStats.leftMenu][i].value.envs[k].name;
                        }
                    }
                }
                break;
            case 'service':
                for (var j in stats.leftMenus[stats.menuStats.leftMenu]) {
                    if (stats.leftMenus[stats.menuStats.leftMenu][j].id == input) {
                        return stats.leftMenus[stats.menuStats.leftMenu][j].name;
                    }
                }
                break;
            default:
                return false;
        }
    };
}]);
