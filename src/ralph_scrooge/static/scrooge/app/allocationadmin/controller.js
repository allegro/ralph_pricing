'use strict';

var scrooge = angular.module('scrooge.controller.allocationadmin', []);

scrooge.controller('allocationAdminCtrl', ['$scope', '$routeParams', '$http', 'stats', function ($scope, $routeParams, $http, stats) {
    stats.breadcrumbs = ['tab'];
    stats.refreshCurrentSubpage = function () {
        stats.getAllocationAdminData();
    };
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Allocations Admin';
    }
    $scope.stats.menuStats.subpage.change = 'allocationadmin';
    $scope.stats.refreshData();
}]);
