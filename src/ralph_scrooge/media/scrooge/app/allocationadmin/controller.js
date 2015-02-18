'use strict';

var scrooge = angular.module('scrooge.controller.allocationadmin', []);

scrooge.controller('allocationAdminCtrl', ['$scope', '$routeParams', '$http', 'stats', function ($scope, $routeParams, $http, stats) {
    if (typeof($routeParams.tab) !== undefined) {
        stats.currentTab = $routeParams.tab;
    }
    stats.breadcrumbs = ['tab'];
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Allocations Admin';
    }
    stats.refreshCurrentSubpage = function () {
        stats.getAllocationAdminData();
    };
    $scope.stats.menuStats.subpage.change = 'allocationadmin';
    $scope.stats.refreshData();
}]);
