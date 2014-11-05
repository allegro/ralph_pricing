'use strict';

var scrooge = angular.module('scrooge.controllers', ['scrooge.services']);

scrooge.controller('SubMenuCtrl', ['$scope', '$location', 'SubMenu', function ($scope, $location, SubMenu) {
    $scope.stats.subMenus = SubMenu.items.get();
    $scope.stats.subMenus.$promise.then(function (subMenus) {
        subMenus.forEach(function (element) {
            if (element.name == $scope.stats.currentSubMenu) {
                $scope.stats.currentSubMenu = element;
            }
        });
    });
    $scope.setActive = function(obj) {
        if (obj.href.charAt(0) == '#') {
            $location.path(obj.href.slice(1));
        } else {
            window.location.href = window.location.protocol + '//' + (window.location.host + obj.href);
        }

        $scope.stats.currentSubMenu = obj;
        if ($scope.stats.inArray($scope.stats.currentLeftMenu, $scope.stats.currentSubMenu.leftMenu) === false) {
            $scope.stats.currentLeftMenu = $scope.stats.getFirstExistMenu();
        }
    };
}]);
