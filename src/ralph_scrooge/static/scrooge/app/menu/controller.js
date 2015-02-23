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
    };
}]);
