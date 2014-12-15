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
    $scope.changeLeftMenu = function (leftMenuName) {
        stats.menuStats.leftMenu.change = leftMenuName;
        stats.refreshData();
        if (leftMenuName === 'services') {
            stats.breadcrumbs = ['tab', 'service', 'env'];
        }
        else if (leftMenuName === 'teams') {
            stats.breadcrumbs = ['tab', 'teams'];
        }
    };
    $scope.changeTeam = function (team) {
        if (stats.menuStats.team.current != team.name) {
            stats.menuStats.team.change = team.id;
            stats.refreshData();
        }
    };
    $scope.setActive = function(obj) {
        if (obj.href.charAt(0) == '#') {
            $location.path(obj.href.slice(1));
        } else {
            window.location.href = window.location.protocol + '//' + (window.location.host + obj.href);
        }

        $scope.stats.currentSubMenu = obj;
        if ($scope.stats.inArray($scope.stats.menuStats.leftMenu, $scope.stats.currentSubMenu.leftMenu) === false) {
            $scope.stats.menuStats.leftMenu.current = $scope.stats.getFirstExistMenu();
        }
    };
}]);
