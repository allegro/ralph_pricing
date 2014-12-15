'use strict';

var scrooge = angular.module('scrooge.filter', []);

scrooge.filter('breadcrumbs', ['stats', function(stats) {
    return function(input, scope) {
        switch(scope) {
            case 'env':
              var currentLeftMenu = stats.menuStats.leftMenu.current;
                for (var menuIdx in stats.leftMenus[currentLeftMenu]) {
                    var envsOfService = stats.leftMenus[currentLeftMenu][menuIdx].value.envs
                    for (var envIdx in envsOfService) {
                        if (envsOfService[envIdx].id == input) {
                            return envsOfService[envIdx].name;
                        }
                    }
                }
                break;
            case 'service':
                var currentLeftMenu = stats.menuStats.leftMenu['current'];
                for (var menuIdx in stats.leftMenus[currentLeftMenu]) {
                    var menuItem = stats.leftMenus[currentLeftMenu][menuIdx];
                    if (menuItem.id == input) {
                        return menuItem.name;
                    }
                }
                break;
            case 'teams':
                for (var teamIdx in stats.leftMenus.teams) {
                    var teamObj = stats.leftMenus.teams[teamIdx];
                    console.log('team', teamIdx, stats.leftMenus.teams, teamObj)
                    console.log(teamObj.id, stats.menuStats.team.current);
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
