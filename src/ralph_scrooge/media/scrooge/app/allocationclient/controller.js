'use strict';

var scrooge = angular.module('scrooge.controller.allocationclient', []);

scrooge.controller('allocationClientCtrl', ['$scope', '$routeParams', '$http', 'menuService', 'menuCalendar', 'stats', function ($scope, $routeParams, $http, menuService, menuCalendar, stats) {
    stats.breadcrumbs = ['tab', 'service', 'env'];
    if ($scope.stats.currentSubMenu === false) {
        $scope.stats.currentSubMenu = 'Allocations';
    }
    stats.refreshCurrentSubpage = function () {
        stats.getAllocationClientData();
    };
    $scope.addRow = function (costList) {
        costList.push({'service': false, 'value': 0});
    };
    $scope.removeRow = function (index, currentList) {
        if (currentList.length >= 2) {
            currentList.splice(index, 1);
        }
    };
    $scope.getTotal = function (tab) {
        var rows_with_data = stats.currentTabs[tab];
        if (typeof rows_with_data !== 'undefined') {
            var count = 0;
            rows_with_data.rows.forEach(function (element) {
                count += Number(element.value, 10);
            });
            return isNaN(count) ? 0.00 : count;
        }
        return 0.00
    }
    $scope.changeTab = function (tab) {
        stats.currentTab = tab;
    };
    $scope.stats.menuStats.subpage.change = 'allocationclient';
    $scope.stats.refreshData();
}]);
