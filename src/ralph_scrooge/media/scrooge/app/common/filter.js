'use strict';

var scrooge = angular.module('scrooge.filter', []);

scrooge.filter('breadcrumbs', ['stats', function(stats) {
    /**
     * Breadcrumbs is composed based on data from stats.menuStats.
     * There we have only a numbers. For example service id or team id.
     * This filter change number to string.
     */
    return function(input, scope) {
        var currentLeftMenu, menuIdx;
        switch(scope) {
            case 'env':
                currentLeftMenu = stats.menuStats.leftMenu.current;
                for (menuIdx in stats.leftMenus[currentLeftMenu]) {
                    var envsOfService = stats.leftMenus[currentLeftMenu][menuIdx].value.envs;
                    for (var envIdx in envsOfService) {
                        if (envsOfService[envIdx].id == input) {
                            return envsOfService[envIdx].name;
                        }
                    }
                }
                break;
            case 'service':
                currentLeftMenu = stats.menuStats.leftMenu['current'];
                for (menuIdx in stats.leftMenus[currentLeftMenu]) {
                    var menuItem = stats.leftMenus[currentLeftMenu][menuIdx];
                    if (menuItem.id == input) {
                        return menuItem.name;
                    }
                }
                break;
            case 'teams':
                for (var teamIdx in stats.leftMenus.teams) {
                    var teamObj = stats.leftMenus.teams[teamIdx];
                    if (teamObj.id === stats.menuStats.team.current) {
                        return teamObj.name;
                    }
                }
                break;
            case 'tab':
                var tabObj = stats.currentTabs[stats.currentTab];
                if (tabObj) {
                    return tabObj.name;
                }
                break;
            default:
                return false;
        }
    };
}]);
