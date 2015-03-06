'use strict';

var scrooge = angular.module('scrooge.controller.menu', ['scrooge.service']);

scrooge.controller('SubMenuCtrl', ['$scope', '$location', 'stats', 'SubMenu', function ($scope, $location, stats, SubMenu) {
    $scope.stats.subMenus = SubMenu.items.get();
    $scope.stats.subMenus.$promise.then(function (subMenus) {
        subMenus.forEach(function (element) {
            if (element.name == $scope.stats.currentSubMenu) {
                $scope.stats.currentSubMenu = element;
            }
        });
    });

    /**
     * Change left menu based on given leftMenuName.
     * @param {string} leftMenuName - Name of left menu.
     */
    $scope.changeLeftMenu = function (leftMenuName) {
        stats.menuStats.leftMenu.change = leftMenuName;
        switch(leftMenuName) {
            case 'services':
                stats.breadcrumbs = ['tab', 'service', 'env'];
                break;
            case 'teams':
                stats.breadcrumbs = ['tab', 'teams'];
                break;
            default:
                break;
        }
        stats.refreshData();
    };

    /**
     * Change team from left menu.
     * @param {object} team - Dict with data like team id etc.
     */
    $scope.changeTeam = function (team) {
        if (stats.menuStats.team.current != team.name) {
            stats.menuStats.team.change = team.id;
            stats.refreshData();
        }
    };

    /**
     * Change subpage.
     * @param {object} team - Dict with data specified for new subpage.
     */
    $scope.setActive = function(obj) {
        if (obj.href.charAt(0) == '#') {
            $location.path(obj.href.slice(1));
        } else {
            window.location.href = window.location.protocol + '//' + (window.location.host + obj.href);
        }

        $scope.stats.currentSubMenu = obj;
        if ($scope.stats.inArray($scope.stats.menuStats.leftMenu, $scope.stats.currentSubMenu.leftMenu) === false) {
            var leftMenu = $scope.stats.getFirstExistMenu();
            $scope.stats.menuStats.leftMenu.current = leftMenu;
            $scope.changeLeftMenu(leftMenu);
        }
        if ($scope.stats.currentSubMenu.auto_choose_env && !$scope.stats.menuStats['env']['current']) {
            $scope.stats.menuStats['env']['change'] = stats.getEnvs($scope.stats.menuStats['service']['current'])[0].id;
        }
    };
}])
.controller('menuStatsAdapterCtrl', ['$scope', 'stats', function($scope, stats){
    $scope.selected = {};
    $scope.startDate = new Date();
    $scope.endDate = new Date();
    $scope.$watch('date', function(newValue) {
        var start = newValue ? newValue.start : false;
        var end = newValue ? newValue.end : false;
        if (start) {
            stats.menuStats['year']['change'] = start.getFullYear();
            stats.menuStats['month']['change'] = start.getMonth() + 1;
            stats.menuStats['day']['change'] = start.getDate();
            stats.menuStats['startDate']['change'] = start;
            stats.refreshData();
        }
        if (end) {
            stats.menuStats['endDate']['change'] = end;
            stats.refreshData();
        }
    }, true);
    $scope.$watch('stats.dates', function(newValue) {
        //TODO: change in REST API - min date instead of list of dates
        if (newValue) {
            var min_year = Object.keys(newValue)[0];
            var min_month = Object.keys(newValue[min_year])[0];
            var min_day = Object.keys(newValue[min_year][min_month])[0];
            $scope.startDate = new Date(min_year, min_month, min_day);
        }
    });
}]);
