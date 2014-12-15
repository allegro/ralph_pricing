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
        if (currentList.length >=2) {
            currentList.splice(index, 1);
        }
    };
    $scope.updateTotal = function (tab) {
        var rows_with_data, _updateTotal = function (obj) {
            var count = 0;
            obj.rows.forEach(function (element) {
                count += parseFloat(element.value, 10);
            });
            obj.total = isNaN(count) ? '' : count;
        };
        rows_with_data = stats.currentTabs[tab];
        if (typeof rows_with_data !== 'undefined') {
            _updateTotal(rows_with_data);
        }
    };
    $scope.changeTab = function (tab) {
        stats.currentTab = tab;
    };
    $scope.stats.menuStats.subpage.change = 'allocationclient';
    $scope.stats.refreshData();
}]);
